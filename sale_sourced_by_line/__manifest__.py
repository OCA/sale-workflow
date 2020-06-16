# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Sourced by Line",
    "summary": "Multiple warehouse source locations for Sale order",
    "version": "15.0.1.0.1",
    "author": "Camptocamp,"
    "Eficent,"
    "SerpentCS,"
    "Info a tout prix,"
    "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_procurement_group_by_line",
    ],
    "data": ["view/sale_view.xml"],
    "installable": True,
}
