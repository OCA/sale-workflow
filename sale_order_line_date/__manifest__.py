# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Date",
    "version": "12.0.1.0.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_view.xml",
        "reports/sale_order_report.xml",
    ],
    "installable": True,
}
