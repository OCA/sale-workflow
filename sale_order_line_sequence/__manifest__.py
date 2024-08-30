# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Sequence",
    "summary": "Propagates SO line sequence to invoices and stock picking.",
    "version": "17.0.1.1.0",
    "author": "ForgeFlow, Serpent CS, Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "data": [
        "views/sale_view.xml",
        "views/report_saleorder.xml",
        "views/account_move_view.xml",
        "views/report_invoice.xml",
    ],
    "depends": ["sale"],
    "installable": True,
}
