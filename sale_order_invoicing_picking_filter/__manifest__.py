# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Invoicing Picking Filter",
    "summary": "Create invoices from sale orders based on the products in pickings.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Sygel, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Invoicing",
    "depends": ["sale_stock", "stock_picking_invoice_link"],
    "data": [
        "wizard/sale_make_invoice_advanced_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
