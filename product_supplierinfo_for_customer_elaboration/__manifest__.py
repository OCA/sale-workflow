# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Supplierinfo for Customers Elaboration",
    "summary": "Allows to define default elaborations and elaboration notes on product"
    " customerinfos",
    "version": "13.0.1.0.0",
    "development_status": "Beta",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["product_supplierinfo_for_customer_sale", "sale_elaboration"],
    "data": ["security/ir.model.access.csv", "views/product_views.xml"],
    "installable": True,
}
