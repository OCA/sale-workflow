# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale MRP BoM Kit Component",
    "summary": "Select and customize kit components on sales order lines",
    "version": "19.0.1.0.0",
    "category": "Sales/Manufacturing",
    "license": "AGPL-3",
    "author": "Eshan Desle, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_mrp_bom",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_order_line_kit_component_security.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
