import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .job_builder import queue_raster_jobs


_logger = logging.getLogger(__name__)


class PosPrinter(models.Model):
    """Adds a 'Community IoT Agent' printer type to the POS Order Printers.

    Core already offers 'iot' (a real IoT Box) and 'epson_epos' (straight to an
    Epson printer). This adds a third option that queues the ticket as a
    community_iot_box job, so the on-site agent can print it on any ESC/POS
    printer.

    Category routing and the Order button are untouched core behaviour.
    """

    _inherit = "pos.printer"

    printer_type = fields.Selection(
        selection_add=[("community_iot", "Use the Community IoT Agent")],
        ondelete={"community_iot": "set default"},
    )
    iot_device_id = fields.Many2one(
        "community_iot_box.iot_device",
        string="IoT Device",
        domain="[('type', 'in', ('ticket_printer', 'standard_printer')), ('active', '=', True)]",
        help="The community IoT device (printer) that should print these tickets.",
    )
    iot_copies = fields.Integer(
        string="Copies",
        default=1,
        help="How many identical tickets to print for each order.",
    )

    @api.model
    def _load_pos_data_fields(self, config):
        # The POS frontend only receives the fields listed here.
        return super()._load_pos_data_fields(config) + ["iot_device_id", "iot_copies"]

    @api.constrains("printer_type", "iot_device_id", "iot_copies")
    def _check_community_iot(self):
        for printer in self:
            if printer.printer_type != "community_iot":
                continue
            if not printer.iot_device_id:
                raise ValidationError(
                    _("Choose an IoT Device for printer '%s'.", printer.name)
                )
            if printer.iot_copies < 1:
                raise ValidationError(_("Copies must be at least 1."))

    def create_iot_print_job(self, raster_base64, width, height):
        """Queue a kitchen/order ticket. Called from the POS frontend."""
        self.ensure_one()
        return queue_raster_jobs(
            self.env,
            self.iot_device_id,
            raster_base64,
            width,
            height,
            name=_("POS ticket - %s", self.name),
            copies=self.iot_copies,
        )
