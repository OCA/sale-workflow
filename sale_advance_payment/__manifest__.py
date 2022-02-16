# Copyright 2015 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Advance Payment",
    "version": "14.0.1.1.1",
    "author": "Comunitea, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Allow to add advance payments on sales and then use them on invoices",
    "depends": ["sale"],
    "data": [
        "wizard/sale_advance_payment_wzd_view.xml",
        "views/sale_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
