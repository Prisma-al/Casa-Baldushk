from odoo import api, fields, models


class PosCategory(models.Model):
    _inherit = "pos.category"

    skip_preparation = fields.Boolean(
        string="Don't Send to Kitchen",
        help="Products in this category, and in any of its child categories, are "
             "never sent to the preparation printers, whatever categories those "
             "printers are configured with.",
    )

    @api.model
    def _load_pos_data_fields(self, config):
        # The flag is read in the POS to decide whether a line reaches a printer.
        return super()._load_pos_data_fields(config) + ["skip_preparation"]
