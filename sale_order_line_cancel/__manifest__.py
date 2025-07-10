# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Cancel",
    "version": "16.0.1.3.0",
    "author": "Okia, BCIM, Camptocamp, ACSONE SA/NV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sales",
    "summary": """Sale cancel remaining""",
    "depends": ["sale_stock"],
    "data": [
        "security/sale_order_line_cancel.xml",
        "wizards/sale_order_line_cancel.xml",
        "views/sale_order.xml",
        "views/sale_order_line.xml",
        "views/res_config_settings_views.xml",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "pre_init_hook": "pre_init_hook",
}
