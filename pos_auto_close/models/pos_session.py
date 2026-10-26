from odoo import models, api, _, fields
from odoo.exceptions import UserError
from odoo.tools import formatLang
import logging

AUTO_CLOSE_DRAFT_NODE = 'pay'
_logger = logging.getLogger(__name__)


class PosSessionExt(models.Model):
    _inherit = "pos.session"

    @api.model
    def _cron_auto_close_sessions(self):
        _logger.info("POS Auto Close: Cron triggered")
        session_ids = self.search([('state', 'in', ('opened', 'closing_control'))]).ids
        _logger.info("POS Auto Close: %s open sessions found", len(session_ids))

        # No savepoints: profisc commits inside its own code, which destroys them.
        # Every step is idempotent, so a failed run is finished by the next one.
        for session_id in session_ids:
            session = self.browse(session_id)
            session = session.with_company(session.company_id)
            try:
                session._auto_close_validate_drafts()
                session._auto_close_cash_out()
                self.env.cr.commit()

                session._auto_close_close()
                self.env.cr.commit()
                _logger.info("POS Auto Close: Session %s closed", session.name)
            except Exception:
                self.env.cr.rollback()   # undo only what wasn't committed yet
                _logger.exception("POS Auto Close: Error closing session %s", session_id)

    # def _auto_close_session(self):
    #     self.ensure_one()
    #     self._auto_close_validate_drafts()
    #     self._auto_close_cash_out()
    #     self._auto_close_close()

    def _auto_close_validate_drafts(self):
        self.ensure_one()
        _logger.info("auto_close_validate_drafts -> u trigeruaaaaaaaaaa")

        # Skip future preset orders: Odoo moves them out of the session on close
        now = fields.Datetime.now()
        is_open_draft = lambda o: o.state == "draft" and not (o.preset_time and o.preset_time > now)

        drafts = self.order_ids.filtered(is_open_draft)
        if not drafts:
            _logger.info("auto_close_validate_drafts -> no drafts found")
            return

        _logger.info("auto_close_validate_drafts -> %s drafts found", len(drafts))

        # par faturat draft qe skan sgje -> duhen cancelu
        empty = drafts.filtered(lambda o: not o.lines)
        if empty:
            empty.action_pos_order_cancel()
            _logger.info("auto_close_validate_drafts -> %s empty drafts cancelled", len(empty))

        to_process = drafts - empty
        if AUTO_CLOSE_DRAFT_NODE == 'cancel':
            to_process.action_pos_order_cancel()
            _logger.info("auto_close_validate_drafts -> %s drafts cancelled", len(to_process))
        else:
            cash_pm = self.config_id.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_pm:
                raise UserError(_("No cash payment method configured on POS '%s'", self.config_id.name))

            for order in to_process:
                remaining = order.amount_total - order.amount_paid
                wizard = self.env['pos.make.payment'].with_context(
                    active_id=order.id,
                    active_ids=order.ids,
                    active_model='pos.order',
                ).create({
                    'payment_method_id': cash_pm.id,
                    'amount': remaining,
                })
                wizard.check()
                _logger.info("auto_close_validate_drafts -> order %s paid %s", order.name, remaining)

        # checku pr siguri
        still_draft = self.order_ids.filtered(is_open_draft)
        if still_draft:
            raise UserError(_("Orders still in draft on session %s: %s",
                              self.name, ", ".join(still_draft.mapped('name'))))

    def _auto_close_cash_out(self):
        self.ensure_one()
        _logger.info("auto_close_cash_out -> u trigeruaaaaaaaaaa")

        if not self.cash_journal_id:
            _logger.info("auto_close_cash_out -> session %s has no cash journal, skipping", self.name)
            return

        # Recompute expected cash: it includes the cash payments made in step 4
        self.invalidate_recordset(['cash_register_balance_end'])
        expected_cash = self.currency_id.round(self.cash_register_balance_end)

        if self.currency_id.compare_amounts(expected_cash, 0) <= 0:
            _logger.info("auto_close_cash_out -> nothing to cash out on %s (%s)", self.name, expected_cash)
            return

        self.sudo().write({'start_at': self.start_at})

        self.try_cash_in_out(
            'out',
            expected_cash,
            _("Automatic cash out"),
            False,  # partner_id
            {'translatedType': _('out')},
        )
        self.message_post(body=_("Automatic cash out: %(amount)s",
                                 amount=formatLang(self.env, expected_cash, currency_obj=self.currency_id)))
        _logger.info("auto_close_cash_out -> %s %s cashed out from %s",
                     expected_cash, self.currency_id.name, self.name)

    def _auto_close_close(self):
        self.ensure_one()
        _logger.info("auto_close_close -> u trigeruaaaaaaaaaa")

        if self.cash_journal_id:
            self.invalidate_recordset(['cash_register_balance_end'])
            counted_cash = self.currency_id.round(self.cash_register_balance_end)
            res = self.post_closing_cash_details(counted_cash)
            self._auto_close_check_result(res, "post_closing_cash_details")

        self.update_closing_control_state_session(_("Closed automatically by POS Auto Close"))

        res = self.close_session_from_ui()
        self._auto_close_check_result(res, "close_session_from_ui")

        if self.state != 'closed':
            raise UserError(_("Session %s is still in state '%s' after closing", self.name, self.state))
        _logger.info("auto_close_close -> session %s closed", self.name)

    def _auto_close_check_result(self, res, step):
        if isinstance(res, dict) and not res.get('successful', True):
            raise UserError(_("%s failed on %s: %s", step, self.name, res.get('message') or res))
