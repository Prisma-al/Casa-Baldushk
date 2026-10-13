from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosSessionExt(models.Model):
    _inherit = "pos.session"

    @api.model
    def _cron_auto_close_sessions(self):
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

    def _auto_close_cash_out(self):
        self.ensure_one()
        _logger.info("auto_close_cash_out -> u trigeruaaaaaaaaaa")

    def _auto_close_close(self):
        self.ensure_one()
        _logger.info("auto_close_close -> u trigeruaaaaaaaaaa")

    def _cron_auto_close_sessions(self):
        _logger.info("cron_auto_close_sessions -> u trigeruaaaaaaaaaa")




