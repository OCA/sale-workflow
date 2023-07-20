# Copyright 2023 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Purchase Procurement Group by Line",
    "summary": "Glue module between 'MTO Sale <-> Purchase'"
    " and 'Sale Procurement Group by Line'",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Hidden",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_purchase_stock",
        "sale_procurement_group_by_line",
    ],
    "installable": True,
    "auto_install": True,
}
