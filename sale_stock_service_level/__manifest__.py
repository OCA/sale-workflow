# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale stock service level",
    "Summary": "Sale different service level per products.",
    "version": "14.0.0.1.0",
    "development_status": "Beta",
    "author": "Pierre Verkest <pierreverkest84@gmail.com>, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Warehouse Management",
    "depends": [
        "sale_stock",
        "stock_service_level",
    ],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/sale_order_views.xml",
    ],
}
