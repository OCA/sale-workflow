# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "RFQ from Quotation",
    "summary": "Create RFQ to capable suppliers from quotation",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_management",
        "purchase_requisition",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "demo": [
        "demo/vendors.xml",
        "demo/product_template.xml",
        "demo/product_supplierinfo.xml",
    ],
}
