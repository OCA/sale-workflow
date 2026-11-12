# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Picking Validation Blocking",
    "summary": "Prevent the validation of delivery orders from the sale order",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_stock"],
    "data": ["views/sale_order.xml", "views/stock_picking.xml"],
}
