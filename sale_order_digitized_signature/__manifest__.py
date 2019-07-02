# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Digitized Signature",
    "version": "12.0.1.0.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "web_widget_digitized_signature",
    ],
    "data": [
        "report/report_saleorder.xml",
        "views/sale_views.xml",
    ],
    "installable": True,
    "development_status": "Stable",
    "maintainers": ["mgosai"],
}
