# Copyright 2015 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Advance Payment",
    "version": "11.0.1.0.0",
    "author": "Comunitea",
    'website': 'www.comunitea.com',
    "category": "Sales",
    "description": """Allow to add advance payments on sales and then use its
 on invoices""",
    "depends": ["sale", "account"],
    "data": ["wizard/sale_advance_payment_wzd_view.xml",
             "views/sale_view.xml",
             "security/ir.model.access.csv"],
    "installable": True,
}
