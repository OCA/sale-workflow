# Copyright 2015 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015-2016 Oihane Crucelaegui <oihane@avanzosc.com>
# Copyright 2015-2020 Tecnativa - Pedro M. Baeza
# Copyright 2016 Lorenzo Battistini
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Type (with stock)",
    "version": "13.0.1.0.0",
    "category": "Sales Management",
    "author": "Grupo Vermon,"
    "AvanzOSC,"
    "Tecnativa,"
    "Agile Business Group,"
    "Niboo,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_stock", "sale_order_type"],
    "data": ["views/sale_order_type_view.xml", "data/default_type.xml"],
    "installable": True,
    "auto_install": True,
}
