# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Elaboration",
    "summary": "Set an elaboration for any sale line",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
        "views/sale_elaboration_views.xml",
        "views/sale_order_views.xml",
        "views/sale_elaboration_report_views.xml",
        "reports/report_deliveryslip.xml",
    ],
}
