# Copyright 2024 SDi Sidoo Soluciones S.L. <www.sidoo.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Margin Update",
    "summary": "Recalculate expected unit price from margin.",
    "author": "Oscar Soto, Sidoo Soluciones S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "version": "16.0.1.0.0",
    "depends": [
        "sale",
        "sales_team",
        "sale_margin",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "wizard/recalculate_price_margin.xml",
    ],
}
