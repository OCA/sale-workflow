# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Sales Fully Delivered and Invoiced",
    "summary": "Useful filters in Sales to know the actual status of deliveries "
    "and invoices",
    "author": "Forgeflow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "version": "13.0.1.0.0",
    "depends": ["sale_stock"],
    "data": ["views/sale_views.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
