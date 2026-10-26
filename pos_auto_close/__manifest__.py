{
    "name": "POS Auto Close",
    "summary": "By activating this module POS will validate all draft orders, do the cash out process and close session at the specified time in the cron job file!",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "author": "Fabio",
    "depends": ["point_of_sale", "profisc"],
    "data": [
        "data/ir_cron.xml"
    ],
    "installable": True,
    "application": False
}