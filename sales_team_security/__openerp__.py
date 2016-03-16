# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sales teams security",
    "version": "9.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "sales_team",
        "sale",
        "crm",
    ],
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Elico Corp, "
              "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "installable": True,
    "data": [
        'security/sales_team_security.xml',
    ],
    "post_init_hook": "assign_contacts_team",
}
