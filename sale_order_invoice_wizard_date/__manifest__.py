# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Invoice Wizard Date",
    "version": "18.0.1.0.0",
    "summary": """
        Add “invoice date” field when creating multiple order
        invoices to be included in draft invoices
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "category": "Sale",
    "depends": ["sale"],
    "data": ["wizard/sale_make_invoice_advance_views.xml"],
}
