# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Supplierinfo for Customer Sale",
    "version": "12.0.1.1.0",
    "summary": "Loads in every sale order line the customer code defined "
               "in the product",
    "author": "Agile Business Group,Vauxoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "product_supplierinfo_for_customer"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_view.xml",
    ],
    "installable": True,
}
