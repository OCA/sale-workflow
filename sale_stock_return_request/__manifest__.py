# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Stock Return Request",
    "version": "14.0.1.1.1",
    "category": "Stock",
    "website": "https://github.com/OCA/sale-workflow",
    "development_status": "Beta",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock", "stock_return_request"],
    "data": ["views/sale_order_views.xml", "views/sale_return_request_views.xml"],
}
