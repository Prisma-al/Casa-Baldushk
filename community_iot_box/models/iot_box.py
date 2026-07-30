import secrets

from odoo import api, fields, models


class CommunityIotBox(models.Model):
    _name = "community_iot_box.iot_box"
    _description = "Community IoT Box"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    token = fields.Char(
        string="IoT Token",
        help="Authentication token used by the IoT Box to communicate with Odoo.",
    )

    box_uid = fields.Char(
        string="Agent UID",
        help="Unique identifier reported by the IoT Box (by the Python agent).",
    )
    hostname = fields.Char(
        string="Hostname",
        help="Hostname reported by the IoT Box.",
    )
    ip_address = fields.Char(
        string="Last IP",
        help="Last known IP address of the IoT Box.",
    )
    mac_address = fields.Char(
        string="MAC Address",
        help="MAC address reported by the IoT Box.",
    )
    agent_version = fields.Char(
        string="Agent Version",
        help="Version of the IoT agent installed on the Raspberry Pi / host.",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("online", "Online"),
            ("offline", "Offline"),
            ("error", "Error"),
        ],
        string="Status",
        default="draft",
        required=True,
        help="Overall state of the IoT Box according to the last heartbeat.",
    )
    last_seen = fields.Datetime(
        string="Last Seen",
        help="Date and time of the last heartbeat received from the IoT Box.",
    )
    config_version = fields.Integer(
        string="Config Version",
        default=1,
        help="Configuration version number used to synchronize with the agent.",
    )

    device_ids = fields.One2many(
        "community_iot_box.iot_device",
        "box_id",
        string="Devices",
    )
    device_count = fields.Integer(
        string="Devices Count",
        compute="_compute_device_count",
        store=False,
    )
    job_ids = fields.One2many(
        "community_iot_box.iot_job",
        "box_id",
        string="IoT Jobs",
    )
    job_count = fields.Integer(
        string="Jobs Count",
        compute="_compute_job_count",
        store=False,
    )

    @api.depends("device_ids")
    def _compute_device_count(self):
        for box in self:
            box.device_count = len(box.device_ids)

    @api.depends("job_ids")
    def _compute_job_count(self):
        for box in self:
            box.job_count = len(box.job_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("token"):
                vals["token"] = self._new_token()
        return super().create(vals_list)

    def _new_token(self):
        Box = self.sudo().with_context(active_test=False)
        while True:
            token = secrets.token_urlsafe(32)
            domain = [("token", "=", token)]
            if self.ids:
                domain.append(("id", "not in", self.ids))
            if not Box.search(domain, limit=1):
                return token

    def action_generate_token(self):
        for box in self:
            box.token = box._new_token()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "IoT Token",
                "message": "Token generated successfully.",
                "type": "success",
                "sticky": False,
            },
        }

    def _increment_config_version(self):
        for box in self.sudo():
            box.write({"config_version": (box.config_version or 0) + 1})

    def action_open_devices(self):
        self.ensure_one()
        action = self.env.ref("community_iot_box.action_community_iot_devices").read()[0]
        action["domain"] = [("box_id", "=", self.id)]
        action["context"] = {"default_box_id": self.id}
        action["view_mode"] = "list,form"
        return action

    def action_open_jobs(self):
        self.ensure_one()
        action = self.env.ref("community_iot_box.action_community_iot_jobs").read()[0]
        action["domain"] = [("box_id", "=", self.id)]
        action["context"] = {"default_box_id": self.id}
        action["view_mode"] = "list,form"
        return action

    def action_test_connection(self):
        self.ensure_one()
        if not self.active:
            return self._notification(
                title="Test Connection",
                message="The IoT Box is archived. Restore it to run tests.",
                level="warning",
            )

        if not self.token:
            return self._notification(
                title="Test Connection",
                message="The IoT Box has no token. Generate one before testing the connection.",
                level="warning",
            )

        active_devices = self.device_ids.filtered("active")
        if not self.last_seen:
            return self._notification(
                title="Test Connection",
                message=(
                    "No heartbeat recorded yet. Start the agent and wait a few seconds. "
                    "No print job was created."
                ),
                level="warning",
            )

        now_dt = fields.Datetime.to_datetime(fields.Datetime.now())
        last_seen_dt = fields.Datetime.to_datetime(self.last_seen)
        elapsed_seconds = 0
        if now_dt and last_seen_dt:
            elapsed_seconds = max(0, int((now_dt - last_seen_dt).total_seconds()))
        elapsed_display = self._format_elapsed_seconds(elapsed_seconds)

        last_seen_local = fields.Datetime.context_timestamp(self, self.last_seen)
        last_seen_display = (
            last_seen_local.strftime("%Y-%m-%d %H:%M:%S")
            if last_seen_local
            else str(self.last_seen)
        )

        if self.state == "online" and elapsed_seconds <= 60:
            return self._notification(
                title="Test Connection",
                message=(
                    f"Connection OK. State: {self.state}. Last heartbeat {elapsed_display} ago "
                    f"({last_seen_display}). Active devices: {len(active_devices)}. "
                    "No print job was sent."
                ),
                level="success",
            )

        return self._notification(
            title="Test Connection",
            message=(
                f"Connection not verified: state={self.state}, last heartbeat {elapsed_display} ago "
                f"({last_seen_display}). Active devices: {len(active_devices)}. "
                "No print job was sent."
            ),
            level="warning",
        )

    def _notification(self, title, message, level="info"):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "type": level,
                "sticky": False,
            },
        }

    def _test_job_type_for_device(self, device_type):
        mapping = {
            "ticket_printer": "test_ticket",
            "standard_printer": "test_ticket",
            "label_printer": "test_label",
            "drawer": "test_drawer",
        }
        return mapping.get(device_type, "test_ticket")

    def _build_generic_test_ticket(self, device):
        self.ensure_one()
        company_name = (self.company_id.name or "COMPANY").upper()
        box_name = self.name or "IoT Box"
        device_name = device.name or device.device_key or "Device"
        now_local = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        dt_str = now_local.strftime("%Y-%m-%d %H:%M:%S")

        width = device._get_ticket_text_width() if hasattr(device, "_get_ticket_text_width") else 42

        separator = "-" * width
        heavy_separator = "=" * width
        type_label = dict(device._fields["type"].selection).get(device.type, device.type or "-")
        backend_label = dict(device._fields["backend"].selection).get(
            device.backend,
            device.backend or "-",
        )
        interface_label = dict(device._fields["interface"].selection).get(
            device.interface,
            device.interface or "-",
        )

        lines = [
            heavy_separator,
            self._center_text(company_name, width),
            self._center_text("IoT BOX COMMUNITY", width),
            self._center_text("TEST TICKET", width),
            heavy_separator,
            self._label_value_line("Date/Time", dt_str, width),
            self._label_value_line("IoT Box", box_name, width),
            self._label_value_line("Hostname", self.hostname or "-", width),
            self._label_value_line("Agent UID", self.box_uid or "-", width),
            self._label_value_line("IP", self.ip_address or "-", width),
            self._label_value_line("Device", device_name, width),
            self._label_value_line("Device Key", device.device_key or "-", width),
            self._label_value_line("Type", type_label, width),
            self._label_value_line("Backend", backend_label, width),
            self._label_value_line("Interface", interface_label, width),
            separator,
            self._format_ticket_item("1", "DEMO PRODUCT", 10.00, width),
            self._format_ticket_item("1", "ANOTHER DEMO PRODUCT", 25.00, width),
            separator,
            self._format_ticket_amount("TOTAL", 35.00, width),
            separator,
            self._center_text("If you can read this, printing works.", width),
            self._center_text("Thanks for using IoT Box Community", width),
            heavy_separator,
        ]

        if width >= 80:
            lines = ["", "", *lines, "", ""]

        return lines

    def _format_ticket_item(self, qty, description, amount, width):
        left = f"{qty} x {description}"
        right = f"{amount:,.2f}"
        max_left = max(1, width - len(right) - 1)
        left = self._truncate_text(left, max_left)
        space_count = max(1, width - len(left) - len(right))
        return f"{left}{' ' * space_count}{right}"

    def _format_ticket_amount(self, label, amount, width):
        left = str(label)
        right = f"{amount:,.2f}"
        max_left = max(1, width - len(right) - 1)
        left = self._truncate_text(left, max_left)
        space_count = max(1, width - len(left) - len(right))
        return f"{left}{' ' * space_count}{right}"

    def _label_value_line(self, label, value, width):
        prefix = f"{label}: "
        available = max(5, width - len(prefix))
        safe_value = self._truncate_text(value or "-", available)
        return f"{prefix}{safe_value}"

    def _center_text(self, text, width):
        return self._truncate_text(text or "", width).center(width)

    def _truncate_text(self, text, max_length):
        raw = str(text or "")
        if len(raw) <= max_length:
            return raw
        if max_length <= 3:
            return raw[:max_length]
        return f"{raw[: max_length - 3]}..."

    def _format_elapsed_seconds(self, seconds):
        total = max(0, int(seconds or 0))
        if total < 60:
            return f"{total}s"
        minutes, rem = divmod(total, 60)
        if minutes < 60:
            return f"{minutes}m {rem}s"
        hours, rem_min = divmod(minutes, 60)
        return f"{hours}h {rem_min}m"
