# Copyright 2022 Ooops - Ashish Hirpara
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order General Discount Triple",
    "summary": "General discount per sale order with triple",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Ashish Hirpara, Ooops, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["ashishhirapara"],
    "installable": True,
    "depends": ["sale", "sale_order_general_discount", "sale_triple_discount"],
    "data": [
        "views/res_config_settings.xml",
    ],
}
