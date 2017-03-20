# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Covenant",
    "summary": "Drive behavior on sale according to commercial conditions",
    "version": "10.0.1.0.0",
    "category": "Sale",
    "website": "https://www.akretion.com",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        'base_onchange_rule',
        'sale',
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/covenant_data.xml',
        'demo/onchange.rule.csv',
        'demo/onchange.rule.line.csv',
        'views/covenant_view.xml',
        'views/partner_view.xml',
        'views/sale_view.xml',
    ],
    "installable": True,
}
