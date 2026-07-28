# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Line Client Order Reference",
    "summary": "Customer Reference on Sale Order Lines and Invoice Lines",
    "version": "18.0.2.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "reports/report_invoice_document.xml",
        "reports/report_saleorder_document.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
