from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    is_draft = fields.Boolean(string="POS Draft", default=False)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        if "is_draft" not in fields_list:
            fields_list.append("is_draft")
        return fields_list

    @api.model
    def _order_fields(self, ui_order):
        vals = super()._order_fields(ui_order)
        if ui_order.get("is_draft"):
            vals["state"] = "draft"
            vals["to_invoice"] = False
        return vals

    def _process_order(self, order, existing_order):
        order_id = super()._process_order(order, existing_order)

        data = order.get("data", order) if isinstance(order, dict) else {}
        if data.get("is_draft"):
            self.browse(order_id).write({"state": "draft", "to_invoice": False})
        return order_id
