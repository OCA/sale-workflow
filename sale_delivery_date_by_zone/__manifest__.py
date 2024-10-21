# Copyright 2023 Ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Sale Delivery Date By Zone",
    "summary": "Bridge module between Sale Delivery Date and Partner Delivery Zone "
    "User can set delivery information by zone and use it on all partners in that zone.",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Ooops404, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "partner_delivery_zone",
        "sale_delivery_date",
        "stock_partner_delivery_window",
        "stock_warehouse_calendar",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/partner_delivery_zone_views.xml",
    ],
    "development_status": "Alpha",
}
