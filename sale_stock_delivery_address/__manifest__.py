# Copyright 2020-21 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Stock Delivery Address",
    "version": "16.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "depends": ["sale_stock", "sale_procurement_group_by_line"],
    "data": ["views/sale_order_view.xml", "views/res_partner_view.xml"],
    "installable": True,
}
