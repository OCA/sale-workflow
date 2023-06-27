# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Subscription management",
    "summary": "Generate recurring invoices.",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Subscription Management",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "author": "Domatix, Odoo Community Association (OCA)",
    "depends": ["sale_management", "account"],
    "data": [
        "views/product_template_views.xml",
        "views/sale_subscription_views.xml",
        "views/sale_subscription_stage_views.xml",
        "views/sale_subscription_tag_views.xml",
        "views/sale_subscription_template_views.xml",
        "views/sale_order_views.xml",
        "views/res_partner_views.xml",
        "data/ir_cron.xml",
        "data/sale_subscription_data.xml",
        "wizard/close_subscription_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
}
