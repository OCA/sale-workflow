# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sale Product Set Packaging Quantity",
    "summary": "Manage packaging and quantities on product set lines",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_product_set", "sale_stock"],
    "data": ["views/product_set.xml", "views/product_set_line.xml"],
}
