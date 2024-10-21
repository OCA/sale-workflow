# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "sale_order_line_date_next_reception",
    "summary": "Next reception Date on sale order line",
    "version": "14.0.1.0.0",
    "category": "Sale",
    "author": "Akretion,  Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
        "product_next_reception_date",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
}
