from odoo import fields, models


class ProductProduct(models.Model):
    # esht marr product.product se pos-i puno me kete model dhe jo me product.template
    _inherit = "product.product"

    # ktu marrim vleren e atij checkut per produkt  qe t bejm sortin n front
    pos_is_favorite = fields.Boolean(
        related="product_tmpl_id.is_favorite",
        readonly=True,
        store=False,
        string="POS Favorite",
    )

    # ky eshte nje funksion ne odoo 18 qe i thote posit se cilat fusha duhen derguar ne front
    def _load_pos_data_fields(self, config_id):
        fields_to_load = super()._load_pos_data_fields(config_id)
        if "pos_is_favorite" not in fields_to_load:
            fields_to_load.append("pos_is_favorite")
        return fields_to_load
