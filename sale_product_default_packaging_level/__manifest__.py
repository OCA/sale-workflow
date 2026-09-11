# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Product Default Packaging Level",
    "summary": """This module allows to show the product default packaging""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale",
        "product_packaging_level",
    ],
    "data": ["views/sale_order.xml"],
    "assets": {
        # To let it available on frontend too
        # (see website_sale_product_default_packaging_level module)
        "web.assets_frontend": [
            "sale_product_default_packaging_level/static/src/**/*",
        ],
        "web.assets_backend": [
            "sale_product_default_packaging_level/static/src/**/*",
        ],
    },
}
