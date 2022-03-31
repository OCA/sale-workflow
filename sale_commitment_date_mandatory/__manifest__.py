# © 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale commitment date mandatory",
    "version": "14.0.1.1.0",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Set commitment data mandatory and don't allow"
    "to add lines unless this field is filled",
    "depends": ["sale"],
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "views/res_config_settings.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
