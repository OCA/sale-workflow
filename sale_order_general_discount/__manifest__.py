# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order General Discount",
    "summary": "General discount per sale order",
    "version": "15.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": ["views/sale_order_view.xml", "views/res_partner_view.xml"],
}
