import logging

from datetime import timedelta

from odoo import api, fields, models


_logger = logging.getLogger(__name__)

# Fallbacks used when the matching ir.config_parameter is missing.
DEFAULT_PROCESSING_TIMEOUT_MINUTES = 5
DEFAULT_MAX_POLL_ATTEMPTS = 3


class CommunityIotJob(models.Model):
    _name = "community_iot_box.iot_job"
    _description = "Community IoT Job"

    name = fields.Char()
    box_id = fields.Many2one("community_iot_box.iot_box", string="IoT Box")
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("done", "Done"),
            ("error", "Error"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        help="Internal job state (pending/processing/done/error/cancelled).",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="box_id.company_id",
        store=True,
        readonly=True,
    )
    device_id = fields.Many2one(
        "community_iot_box.iot_device",
        string="Device",
    )
    device_key = fields.Char(
        string="Device Key",
        help="Logical identifier of the device targeted by this job.",
    )
    job_type = fields.Selection(
        selection=[
            ("ticket_print", "Ticket Print"),
            ("cash_drawer", "Cash Drawer"),
            ("open_cashdrawer", "Open Cash Drawer"),
            ("label_print", "Label Print"),
            ("label_print_zpl", "Label Print ZPL"),
            ("test_ticket", "Test Ticket"),
            ("test_label", "Test Label"),
            ("test_drawer", "Test Drawer"),
        ],
        string="Job Type",
        required=True,
        default="ticket_print",
    )
    payload = fields.Text(
        string="Payload",
        help="Serialized JSON content with the data the IoT agent needs.",
    )
    result_status = fields.Selection(
        selection=[
            ("none", "Not Reported"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("error", "Error"),
        ],
        string="Result Status",
        default="none",
    )
    result_message = fields.Text(string="Result Message")
    agent_log = fields.Text(string="Agent Log")
    error_code = fields.Char(string="Error Code")
    error_message = fields.Text(string="Error Message")
    origin_model = fields.Char(
        string="Origin Model",
        help="Technical name of the source model (for example 'pos.order', 'stock.picking').",
    )
    origin_id = fields.Integer(
        string="Origin Record ID",
        help="ID of the source record related to this job.",
    )
    processed_at = fields.Datetime(
        string="Processed At",
        help="Date and time the job finished (success or error).",
    )
    polled_at = fields.Datetime(
        string="Polled At",
        help="Date and time an agent last claimed this job through /jobs/poll.",
    )
    poll_count = fields.Integer(
        string="Poll Attempts",
        default=0,
        help="How many times an agent has claimed this job. Used to stop a job "
        "from being requeued forever when the agent keeps dying mid-print.",
    )

    @api.model
    def _get_processing_timeout_minutes(self):
        value = self.env["ir.config_parameter"].sudo().get_param(
            "community_iot_box.job_processing_timeout_minutes"
        )
        try:
            timeout = int(value)
        except (TypeError, ValueError):
            return DEFAULT_PROCESSING_TIMEOUT_MINUTES
        return timeout if timeout > 0 else DEFAULT_PROCESSING_TIMEOUT_MINUTES

    @api.model
    def _get_max_poll_attempts(self):
        value = self.env["ir.config_parameter"].sudo().get_param(
            "community_iot_box.job_max_poll_attempts"
        )
        try:
            attempts = int(value)
        except (TypeError, ValueError):
            return DEFAULT_MAX_POLL_ATTEMPTS
        return attempts if attempts > 0 else DEFAULT_MAX_POLL_ATTEMPTS

    @api.model
    def _cron_requeue_stale_jobs(self):
        """Rescue jobs stuck in 'processing'.

        /jobs/poll flips a job to 'processing' as soon as an agent claims it. If
        that agent then crashes, loses the network or is killed mid-print, the
        job would otherwise stay 'processing' forever and the ticket is silently
        lost. Put it back to 'pending' so another poll picks it up, and give up
        with an explicit error once it has burned through its attempts.
        """
        timeout = self._get_processing_timeout_minutes()
        max_attempts = self._get_max_poll_attempts()
        now = fields.Datetime.now()
        cutoff = now - timedelta(minutes=timeout)

        stale = self.search(
            [
                ("state", "=", "processing"),
                "|",
                ("polled_at", "<", cutoff),
                # Jobs polled before polled_at existed, or written directly.
                "&",
                ("polled_at", "=", False),
                ("write_date", "<", cutoff),
            ]
        )
        if not stale:
            return

        exhausted = stale.filtered(lambda job: job.poll_count >= max_attempts)
        retryable = stale - exhausted

        if retryable:
            retryable.write({"state": "pending"})
        if exhausted:
            exhausted.write(
                {
                    "state": "error",
                    "result_status": "error",
                    "error_code": "IOT_JOB_TIMEOUT",
                    "error_message": (
                        f"No result reported by the agent within {timeout} minute(s) "
                        f"after {max_attempts} attempt(s). The job was abandoned."
                    ),
                    "processed_at": now,
                }
            )

        _logger.warning(
            "IoT: requeued %s stale job(s), abandoned %s past %s attempt(s)",
            len(retryable),
            len(exhausted),
            max_attempts,
        )
