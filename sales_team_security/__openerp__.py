# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sales teams security",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "sales_team",
        "sale",
        "crm",
    ],
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://www.tecnativa.com",
    "category": "Sales Management",
    "installable": True,
    "data": [
        'security/sales_team_security.xml',
        'views/res_partner_view.xml',
    ],
    "post_init_hook": "assign_contacts_team",
}
