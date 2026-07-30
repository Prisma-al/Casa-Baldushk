import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .job_builder import queue_raster_jobs


_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    """Customer receipt printing through the community IoT agent.

    Order Printers (pos.printer) handle kitchen tickets. The customer receipt is
    separate: the POS prints it through hardware_proxy.printer, which is what
    PosPrinterService.print() reads. Setting a device here attaches our printer
    there, so "Print Receipt" queues an IoT job instead of opening the browser
    print dialog.
    """

    _inherit = "pos.config"

    community_iot_receipt_device_id = fields.Many2one(
        "community_iot_box.iot_device",
        string="Receipt IoT Printer",
        domain="[('type', 'in', ('ticket_printer', 'standard_printer')), ('active', '=', True)]",
        help="Print customer receipts on this community IoT device. "
             "Leave empty to keep using the browser print dialog.",
    )
    community_iot_receipt_copies = fields.Integer(
        string="Receipt Copies",
        default=1,
        help="How many copies of each customer receipt to print.",
    )

    # NOTE: deliberately no _load_pos_data_fields override here.
    # pos.load.mixin returns [], and read([]) means "all fields", so pos.config
    # ships every field to the POS already - including the two added above.
    # Overriding it to return a short list would restrict the load and break
    # core, which reads e.g. record['use_pricelist'] in _load_pos_data_read.
    # pos.printer is different: it returns an explicit field list, so there the
    # override is required.

    @api.constrains("community_iot_receipt_copies")
    def _check_community_iot_receipt_copies(self):
        for config in self:
            if config.community_iot_receipt_device_id and config.community_iot_receipt_copies < 1:
                raise ValidationError(_("Receipt copies must be at least 1."))

    def create_iot_receipt_job(self, raster_base64, width, height, order_ref=None,
                               order_id=None):
        """Queue a customer receipt. Called from the POS frontend."""
        self.ensure_one()
        return queue_raster_jobs(
            self.env,
            self.community_iot_receipt_device_id,
            raster_base64,
            width,
            height,
            name=_("POS receipt - %s", order_ref or self.name),
            copies=self.community_iot_receipt_copies,
            origin_model="pos.order" if order_id else None,
            origin_id=order_id,
        )
