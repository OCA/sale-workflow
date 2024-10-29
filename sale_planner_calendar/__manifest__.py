# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale planner calendar",
    "summary": "Sale planner calendar",
    "version": "16.0.2.0.0",
    "development_status": "Beta",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["calendar", "sale", "sale_payment_sheet"],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_planner_calendar_security.xml",
        "data/sale_planner_calendar_action_server.xml",
        "data/sale_planner_calendar_cron.xml",
        "data/sale_planner_calendar_data.xml",
        "views/calendar_event_type_view.xml",
        "views/calendar_view.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_view.xml",
        "views/sale_planner_calendar_event_view.xml",
        "views/sale_planner_calendar_issue_type_view.xml",
        "views/sale_planner_calendar_summary_view.xml",
        "wizard/sale_planner_calendar_reassign.xml",
        "wizard/sale_planner_calendar_wizard.xml",
        # Menu position fixed
        "views/sale_planner_calendar_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_planner_calendar/static/src/xml/categ_icons_widget_template.xml",
            "sale_planner_calendar/static/src/xml/sale_planner_calendar_event_sales.xml",
            "sale_planner_calendar/static/src/scss/sale_planner_calendar.scss",
            "sale_planner_calendar/static/src/js/*.js",
        ],
    },
}
