{
    "name": "POS Community IoT Printing",
    "summary": "Print POS receipts and kitchen tickets through the community IoT agent",
    "description": """
Bridges the Point of Sale to community_iot_box.

Adds a new Order Printer type, "Community IoT Agent". When the POS prints a
receipt or a kitchen ticket to such a printer, the receipt is rasterised in the
browser and queued as an IoT job. The on-site agent picks the job up and sends
it to the printer.

The receipt is sent as an image, exactly as the Epson printer support does, so
the printed result matches the POS receipt design and accented characters
(e.g. Albanian e-diaeresis and c-cedilla) need no printer codepage.
    """,
    "version": "19.0.1.0.0",
    "category": "Sales/Point of Sale",
    "author": "Casa Baldushk",
    "license": "LGPL-3",
    "depends": ["point_of_sale", "community_iot_box"],
    "data": [
        "views/pos_printer_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_community_iot/static/src/js/community_iot_printer.js",
            "pos_community_iot/static/src/js/pos_store_patch.js",
        ],
    },
    "installable": True,
}
