# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order - Ordered Weight",
    "summary": "Add Ordered weights on sale order and sale order line levels",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "author": "GRAP, Xtendoo, Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale"],
    "data": [
        "views/sale_order_view.xml",
        "views/res_config_settings_view.xml",
        "reports/report_sale_order.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
