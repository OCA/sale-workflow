# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Lead Time",
    "summary": "Calculate sale order line customer lead using sale order delivery lead time",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_stock", "lead_time_profile"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
