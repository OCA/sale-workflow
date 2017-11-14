# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Order Action Invoice Create Hook",
    "author": "Eficent, Odoo Community Association (OCA)",
    "version": "11.0.1.0.0",
    "category": "Sale Workflow",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        'sale',
    ],
    "license": 'LGPL-3',
    "post_load": "post_load_hook",
    "installable": True
}
