# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    display_stock_location_ids = fields.Many2many(
        "stock.location",
        string="Sale Order Line Stock Locations",
        help=(
            "Locations to use when computing the stock quantity shown on "
            "sale order lines for this warehouse. If empty, the whole "
            "warehouse is used."
        ),
    )
    display_stock_on_sol = fields.Boolean(
        string="Display stock on Sale Order Line",
    )
