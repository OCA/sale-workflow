# Copyright 2026 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Blanket Order Advanced",
    "summary": "Advanced features: version control, order plans and cost tracking",
    "category": "Sale",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "base_revision",
        "sale_blanket_order",
    ],
    "data": [
        "wizard/sale_blanket_order_advanced_version.xml",
        "wizard/sale_create_order_plan.xml",
        "wizard/sale_make_planned_order.xml",
        "views/blanket_order_plan.xml",
        "views/blanket_order_product.xml",
        "views/blanket_order_service.xml",
        "views/sale_blanket_order.xml",
        "views/res_config_settings_views.xml",
        "data/config_settings.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/sale_blanket_order.xml",
    ],
    "installable": True,
}
