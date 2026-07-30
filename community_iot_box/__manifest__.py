{
    "name": "IoT Box Community",
    "summary": "Manage IoT Boxes and print jobs on Odoo 19 Community.",
    "description": """
Community IoT Box for Odoo 19 Community.

Features:
- IoT Boxes, IoT Devices and IoT Jobs.
- REST API endpoints for external IoT agents.
- Token-based agent registration and heartbeat.
- Job polling and result reporting.
- Support for virtual IoT agents on Windows/Linux.
- Automatic device synchronization from the external agent.

Note: this module is the Odoo-side half only. It stores devices and queues
jobs; an external agent running on the local network must poll the REST API
and drive the actual hardware.
    """,
    "version": "19.0.1.0.0",
    "category": "Technical/IoT",
    "author": "JDA Solutions",
    "website": "https://github.com/julesprog963-stack/Iot_box_community",
    "support": "julesprog963@gmail.com",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "images": [
        "static/description/images/main_screenshot.png",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/iot_menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "community_iot_box/static/src/scss/community_iot_box.scss",
        ],
    },
    "application": True,
    "installable": True,
}
