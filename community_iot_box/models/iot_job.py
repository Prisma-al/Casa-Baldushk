from odoo import api, fields, models


class CommunityIotJob(models.Model):
    _name = "community_iot_box.iot_job"
    _description = "Community IoT Job"

    name = fields.Char()
    box_id = fields.Many2one("community_iot_box.iot_box", string="IoT Box")
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("done", "Done"),
            ("error", "Error"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        help="Internal job state (pending/processing/done/error/cancelled).",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="box_id.company_id",
        store=True,
        readonly=True,
    )
    device_id = fields.Many2one(
        "community_iot_box.iot_device",
        string="Device",
    )
    device_key = fields.Char(
        string="Device Key",
        help="Logical identifier of the device targeted by this job.",
    )
    job_type = fields.Selection(
        selection=[
            ("ticket_print", "Ticket Print"),
            ("cash_drawer", "Cash Drawer"),
            ("open_cashdrawer", "Open Cash Drawer"),
            ("label_print", "Label Print"),
            ("label_print_zpl", "Label Print ZPL"),
            ("test_ticket", "Test Ticket"),
            ("test_label", "Test Label"),
            ("test_drawer", "Test Drawer"),
        ],
        string="Job Type",
        required=True,
        default="ticket_print",
    )
    payload = fields.Text(
        string="Payload",
        help="Serialized JSON content with the data the IoT agent needs.",
    )
    result_status = fields.Selection(
        selection=[
            ("none", "Not Reported"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("error", "Error"),
        ],
        string="Result Status",
        default="none",
    )
    result_message = fields.Text(string="Result Message")
    agent_log = fields.Text(string="Agent Log")
    error_code = fields.Char(string="Error Code")
    error_message = fields.Text(string="Error Message")
    origin_model = fields.Char(
        string="Origin Model",
        help="Technical name of the source model (for example 'pos.order', 'stock.picking').",
    )
    origin_id = fields.Integer(
        string="Origin Record ID",
        help="ID of the source record related to this job.",
    )
    processed_at = fields.Datetime(
        string="Processed At",
        help="Date and time the job finished (success or error).",
    )
