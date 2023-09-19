# Copyright 2023 Ows - Henrik Norlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Book resources from a timeline",
    "summary": "",
    "author": "Ows, Odoo Community Association (OCA)",
    "category": "Appointments",
    "data": [
        "views/product_template_views.xml",
        "views/resource_booking_type_views.xml",
        "views/resource_booking_views.xml",
    ],
    "depends": [
        "sale_resource_booking",
        "web_timeline",
    ],
    "license": "AGPL-3",
    "maintainers": ["ows-cloud"],
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
}
