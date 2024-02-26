# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Discount Display Amount",
    "summary": """
        This addon intends to display the amount of the discount computed on
        sale_order_line and sale_order level""",
    "version": "14.0.2.1.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_management"],
    "data": [
        "views/res_config_settings_view.xml",
        "views/sale_view.xml",
        "report/sale_report_template.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
