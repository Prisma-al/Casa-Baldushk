{
    'name': "Thermal Receipt",

    'summary': "Kitchen preparation receipts grouped by POS category",

    'description': """
Prints the POS preparation ("kitchen") receipt with its lines grouped by POS
category instead of by course, in a large font suitable for thermal printers.
Also adds a thermal HTML invoice report on customer invoices.
    """,

    'author': "Casa Baldushk",
    'website': "https://www.yourcompany.com",

    'category': 'Sales/Point of Sale',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'point_of_sale'],

    # always loaded
    'data': [
        'report/report.xml',
        'report/paperformat.xml',
        'report/report_invoice_thermal_html.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'thermal_receipt/static/src/xml/order_change_receipt_extend.xml',
            'thermal_receipt/static/src/js/order_print_change_patch.js',
        ],
    },
}
