# © 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale order HTML conditions",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Add HTML sale conditions into sale order",
    "depends": ["sale"],
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        # Reports
        "reports/sale_report_templates.xml",
        # Views
        "views/res_company_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
