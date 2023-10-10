# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "sale_line_service_qty_delivered",
    "summary": "Changes the Delivered Quantity (qty_delivered) of a service sale.order.line"
    "if one other sale.order.line is delivered the qty_delivered of the service line"
    "is changed to its Quantity (product_uom_qty)",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Michael Tietz (MT Software) <mtietz@mt-software.de>,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_stock",
        "delivery",
    ],
}
