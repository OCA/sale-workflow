# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Order Client Order Ref Mandatory",
    "summary": """
        Adds required client_order_ref field and reposition it
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "data": [
        "views/sale_order_view.xml",
        "report/sale_order_report_templates.xml",
    ],
    "installable": True,
}
