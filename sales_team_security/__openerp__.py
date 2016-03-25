# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sales teams security",
    "version": "8.0.2.0.0",
    "license": "AGPL-3",
    "depends": [
        "sales_team",
        "sale",
        "crm",
    ],
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "installable": True,
    "data": [
        'security/sales_team_security.xml',
        'views/res_partner_view.xml',
    ],
    "post_init_hook": "assign_contacts_team",
}
