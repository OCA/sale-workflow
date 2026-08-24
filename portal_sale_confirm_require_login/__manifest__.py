# Copyright 2026 Tecnativa S.L. - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Portal Sale Confirm Require Login",
    "summary": (
        "Force login/signup to access quotations via token and require partner "
        "information completion before confirming from the portal"
    ),
    "version": "19.0.1.0.0",
    "category": "Sales",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "portal",
    ],
    "data": [
        "views/portal_templates.xml",
        "views/res_config_settings_views.xml",
        "views/sale_portal_templates.xml",
    ],
}
