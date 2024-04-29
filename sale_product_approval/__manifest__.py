# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Product Approval",
    "summary": """Control whether or not the product can be sold or not
     in the particular state""",
    "version": "17.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Products",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "maintainers": ["dreispt"],
    "development_status": "Alpha",
    "depends": ["product_state", "sale_management", "stock"],
    "data": [
        "security/res_groups.xml",
        "views/menu_items.xml",
        "views/product_exception.xml",
        "views/product_state.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
    ],
    "post_init_hook": "_set_candidate_sale",
}
