from odoo import models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def read_config_open_orders(self, domain, record_ids=[]):
        res = super().read_config_open_orders(domain, record_ids)

        cached_ids = (record_ids or {}).get('pos.order', [])
        if cached_ids:
            stale = self.env['pos.order'].browse(cached_ids).exists().filtered(
                lambda o: o.state != 'draft' and o.session_id.state == 'closed'
            )
            if stale:
                deleted = res['deleted_record_ids'].setdefault('pos.order', [])
                deleted.extend(i for i in stale.ids if i not in deleted)

        return res