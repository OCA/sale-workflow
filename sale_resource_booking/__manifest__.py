# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sell Resource Bookings",
    "summary": "Link resource bookings with sales",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Appointments",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Yajo"],
    "license": "AGPL-3",
    "depends": ["sale", "resource_booking", "web_ir_actions_act_multi"],
    "data": [
        "views/product_attribute_views.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
        "views/resource_booking_type_views.xml",
        "views/resource_booking_views.xml",
        "views/sale_order_views.xml",
        "views/menus.xml",
        "wizards/resource_booking_sale_views.xml",
        "wizards/sale_order_booking_confirm_views.xml",
        "security/ir.model.access.csv",
    ],
}
