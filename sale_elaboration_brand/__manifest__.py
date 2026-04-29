# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product brand in sale elaboration report",
    "summary": "Show product brand in sale elaboration report",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Andrii9090", "sergio-teruel"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_elaboration", "product_brand"],
    "data": ["views/stock_move_report_views.xml"],
}
