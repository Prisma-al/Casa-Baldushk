from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosSessionExt(models.Model):
    _inherit = "pos.session"

    def _cron_auto_close_sessions(self):
        _logger.info("cron_auto_close_sessions -> u trigeruaaaaaaaaaa")


