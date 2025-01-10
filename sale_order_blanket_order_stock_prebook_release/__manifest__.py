# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Blanket Order Stock Prebook Release",
    "summary": """Ensure that the date priotity when releasing"""
    """ qty is the start date of the blanker order""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_order_blanket_order_stock_prebook",
        "stock_available_to_promise_release",
    ],
    "auto_install": True,
    "post_init_hook": "post_init_hook",
}
