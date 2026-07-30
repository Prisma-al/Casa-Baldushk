from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose the pos.config receipt-printer fields in Point of Sale settings.

    Odoo edits pos.config through res.config.settings using related fields named
    pos_<field>, the same way pos_epson_printer_ip is handled in core.
    """

    _inherit = "res.config.settings"

    pos_community_iot_receipt_device_id = fields.Many2one(
        related="pos_config_id.community_iot_receipt_device_id",
        readonly=False,
    )
    pos_community_iot_receipt_copies = fields.Integer(
        related="pos_config_id.community_iot_receipt_copies",
        readonly=False,
    )
