# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Order Line Hide Description",
    "summary": """
        This module hide the description of the sale order lines without
        hiding the sections and notes to avoid a redundant existing
        product field in the case when sale line description won't change
        by company policy.
        It will continue to appear in the reports.
    """,
    "version": "17.0.1.0.0",
    "category": "Sales Management",
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "assets": {
        "web.assets_backend": [
            "sale_order_line_hide_description/static/src/js/sale_order_line_renderer.esm.js",
            "sale_order_line_hide_description/static/src/css/sale_order_line_renderer.css",
        ],
    },
    "installable": True,
}
