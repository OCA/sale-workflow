# Copyright (c) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order line discount Validation",
    "summary": "Review discounts before sales order are printed, sent or confirmed",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "maintainers": ["max3903"],
    "depends": ["sale_management"],
    "data": [
        "data/mail_template.xml",
        "views/res_config_settings_views.xml",
        "views/sale_order.xml",
    ],
}
