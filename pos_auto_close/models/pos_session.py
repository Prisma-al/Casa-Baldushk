from odoo import models, api, _
from odoo.exceptions import UserError
import logging

AUTO_CLOSE_DRAFT_NODE = 'pay'
_logger = logging.getLogger(__name__)

class PosSessionExt(models.Model):
    _inherit = "pos.session"

    @api.model
    def _cron_auto_close_sessions(self):
        _logger.info("POS Auto Close: Cron triggered")
        sessions = self.search([
            ('state', 'in', ('opened', 'closing_control')),
        ])
        _logger.info("POS Auto Close: %s open sessions found", len(sessions))

        for session in sessions:
            session = session.with_company(session.company_id)
            try:
                # save point per te mos shku half-way po ose all-in ose 0
                with self.env.cr.savepoint():
                    session._auto_close_session()
                self.env.cr.commit()
                _logger.info("POS Auto Close: Session %s closed", session.id)
            except Exception:
                _logger.exception("POS Auto Close: Error closing session %s", session.id)

    def _auto_close_session(self):
        self.ensure_one()
        self._auto_close_validate_drafts()
        self._auto_close_cash_out()
        self._auto_close_close()

    def _auto_close_validate_drafts(self):
        self.ensure_one()
        _logger.info("auto_close_validate_drafts -> u trigeruaaaaaaaaaa")
        drafts = self.order_ids.filtered(lambda o: o.state == "draft")
        if not drafts:
            _logger.info("auto_close_validate_drafts -> no drafts found")
            return

        _logger.info("auto_close_validate_drafts -> %s drafts found", len(drafts))

        # par faturat draft qe skan sgje -> duhen cancelu
        empty = drafts.filtered(lambda o: not o.lines)
        if empty:
            empty.action_pos_order_cancel()
            _logger.info("auto_close_validate_drafts -> %s drafts cancelled", len(empty))

        to_process = drafts - empty
        if AUTO_CLOSE_DRAFT_NODE == 'cancel':
            to_process.action_pos_order_cancel()
            _logger.info("auto_close_validate_drafts -> %s drafts cancelled", len(to_process))
        else:
            cash_pm = self.config_id.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_pm:
                raise UserError(_("No cash payment method configured"))

            for order in to_process:
                remaining = order.amount_untaxed - order.amount_paid
                wizard = self.env['pos.make.payment'].with_context(
                    active_id=order.id,
                    active_ids=order.ids,
                    ative_model='pos.order',
                ).create({
                    'payment_method_id': cash_pm.id,
                    'amount': remaining,
                })
                wizard.check()
                _logger.info("auto_close_validate_drafts -> %s drafts paid", len(to_process))

        # checku pr siguri
        still_draft = self.order_ids.filtered(lambda o: o.state == "draft")
        if still_draft:
            raise UserError(_("Some drafts are still open"))

    def _auto_close_cash_out(self):
        self.ensure_one()
        _logger.info("auto_close_cash_out -> u trigeruaaaaaaaaaa")

    def _auto_close_close(self):
        self.ensure_one()
        _logger.info("auto_close_close -> u trigeruaaaaaaaaaa")




