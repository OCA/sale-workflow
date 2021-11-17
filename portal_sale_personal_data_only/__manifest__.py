# Copyright 2018-19 Tecnativa S.L. - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Portal Sale Personal Data Only",
    "version": "13.0.1.0.0",
    "category": "Sale",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "website": "https://www.github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": ["data/portal_sale_security.xml"],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
