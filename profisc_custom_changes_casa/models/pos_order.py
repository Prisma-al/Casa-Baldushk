from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    is_draft = fields.Boolean(string="POS Draft", default=False)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        if "is_draft" not in fields_list:
            fields_list['is_draft'] = 'is_draft'
        return fields_list

    def _process_order(self, order, existing_order):
        order_id = super()._process_order(order, existing_order)

        data = order.get("data", order) if isinstance(order, dict) else {}
        if data.get("is_draft"):
            pos_order = self.browse(order_id)

            pos_order.write({"state": "draft", "to_invoice": False})
        return order_id
