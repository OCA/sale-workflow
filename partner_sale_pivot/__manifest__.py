# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Partner Sale Pivot",
    "summary": "Sales analysis from customer form view",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["ernestotejeda"],
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_report_views.xml",
        "views/res_partner_views.xml",
    ],
}
