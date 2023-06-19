# Copyright 2017-20 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Fixed Discount",
    "summary": "Allows to apply fixed amount discounts in sales orders.",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale", "account_invoice_fixed_discount"],
    "data": [
        "views/sale_order_views.xml",
        "views/account_invoice_views.xml",
        "views/sale_portal_templates.xml",
        "reports/report_sale_order.xml",
    ],
}
