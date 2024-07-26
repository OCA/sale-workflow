# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Type Quotation Number",
    "summary": "Use quotation sequence depending on sale type",
    "version": "15.0.1.2.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_order_type",
        "sale_quotation_number",
    ],
    "data": ["views/sale_order_type_view.xml", "views/sale_views.xml"],
}
