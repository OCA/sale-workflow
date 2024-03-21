# Copyright 2016-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Commercial Partner",
    "summary": "Add stored related field 'Commercial Entity' on sale orders",
    "version": "16.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "license": "AGPL-3",
    "contributors": ["Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>"],
    "depends": ["sale"],
    "data": ["views/sale_order.xml", "views/sale_report.xml"],
    "installable": True,
}
