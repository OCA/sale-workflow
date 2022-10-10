# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Stock Sourcing Address",
    "version": "13.0.1.0.0",
    "author": "ForgeFlow S.L.," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "license": "LGPL-3",
    "depends": ["sale_stock"],
    "data": [
        "security/security.xml",
        "views/sale_order_view.xml",
        "views/account_invoice_view.xml",
    ],
    "installable": True,
}
