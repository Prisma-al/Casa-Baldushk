"""Shared job creation, used by both the kitchen printer and the receipt printer.

Kept in one place so there is exactly one definition of what a POS raster print
job looks like.
"""

import json
import logging

from odoo import _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


def queue_raster_jobs(env, device, raster_base64, width, height, name,
                      copies=1, origin_model=None, origin_id=None):
    """Create one IoT job per requested copy for a rasterised receipt.

    Raises UserError on anything the cashier can act on, so the POS shows a
    dialog instead of silently dropping the ticket.
    """
    if not device:
        raise UserError(_("No IoT Device configured for this printer."))
    if not device.active:
        raise UserError(_("IoT Device '%s' is archived.", device.name))

    box = device.box_id
    if not box or not box.active:
        raise UserError(
            _("IoT Device '%s' is not linked to an active IoT Box.", device.name)
        )
    if not raster_base64:
        raise UserError(_("The receipt produced no printable image."))

    # Reuse the connection details the device model already assembles, so
    # host/port/interface are defined in exactly one place.
    payload = device._build_common_device_payload()
    payload.update({
        "backend": "escpos_raster",
        "raster_base64": raster_base64,
        "raster_width": int(width or 0),
        "raster_height": int(height or 0),
        "open_cashdrawer": False,
    })
    serialized = json.dumps(payload)

    copies = max(1, int(copies or 1))
    vals_list = []
    for index in range(copies):
        suffix = f" ({index + 1}/{copies})" if copies > 1 else ""
        vals_list.append({
            "name": f"{name}{suffix}",
            "box_id": box.id,
            "device_id": device.id,
            "device_key": device.device_key,
            "job_type": "ticket_print",
            "state": "pending",
            "payload": serialized,
            "origin_model": origin_model or False,
            "origin_id": origin_id or False,
        })

    jobs = env["community_iot_box.iot_job"].sudo().create(vals_list)
    _logger.info(
        "POS queued IoT job(s) %s on device %s (%sx%s px, %s cop%s)",
        jobs.ids, device.device_key, width, height, copies,
        "y" if copies == 1 else "ies",
    )
    return {"job_ids": jobs.ids, "job_id": jobs[0].id}
