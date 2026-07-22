from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    is_draft = fields.Boolean(string="Skip Fiscalization (Draft)", default=False)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        if "is_draft" not in fields_list:
            fields_list.append("is_draft")
        return fields_list
