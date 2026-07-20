{
    "name": "POS Front Sort",
    "summary": "Sort POS products by favorite flag and name",
    "description": """
Sort the POS frontend product list by favorite first and then by name.

Odoo 19 already loads the favorite flag and puts favorites on top, but orders
the remaining products by pos_sequence (creation order) rather than by name.
    """,
    "category": "Point of Sale",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_front_sort/static/src/js/sort_product.js",
        ],
    },
}
