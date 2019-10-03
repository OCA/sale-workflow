# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sale Quotation Synchronizer",
    "summary": "Synchronize quotations and quotation templates from products",
    "version": "10.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_quote",
    ],
    "data": [
        "wizards/sale_quotation_synchronizer.xml",
    ],
}
