# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Product Packaging Type Can Be Sold",
    "summary": "Defines packaging types that can be sold",
    "version": "13.0.1.1.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto-install": True,
    "depends": ["product_packaging_can_be_sold", "product_packaging_type"],
    "data": ["views/product_packaging_type.xml"],
}
