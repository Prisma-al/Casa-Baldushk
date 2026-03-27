{
    "name": "POS Front Sort",
    "summary": "Sort POS products by favorite flag and name",
    "description": """
Load the favorite flag from product templates into POS products and sort
the POS frontend product list by favorite first and then by name.
    """,
    "category": "Point of Sale",
    "version": "18.0.1.0.1",
    "license": "LGPL-3",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_front_sort/static/src/js/sort_product.js",
        ],
    },
}
