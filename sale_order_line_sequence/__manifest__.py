# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Sequence",
    "summary": "Propagates SO line sequence to invoices and stock picking.",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, Serpent CS, Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "data": ["views/sale_view.xml", "views/report_saleorder.xml"],
    "depends": ["sale"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
