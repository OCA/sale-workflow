# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Force Invoiced",
    "summary": "Allows to force the invoice status of the sales order to Invoiced",
    "version": "16.0.2.1.1",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "sale",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale", "sales_team"],
    "data": [
        "security/security.xml",
        "view/sale_order.xml",
    ],
    "installable": True,
}
