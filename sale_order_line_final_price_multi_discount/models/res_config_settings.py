# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

from .sale_order_line import POLICY_PARAM, UNLOCK_PARAM


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    final_price_distribution_policy = fields.Selection(
        [
            ("replace", "Replace the discounts"),
            ("append", "Append to the pricelist discounts"),
        ],
        string="Final Price Discounts",
        default="replace",
        config_parameter=POLICY_PARAM,
        help="Replace: the final price becomes a single discount. Append: the "
        "discounts of the pricelist rule are kept and one more discount is "
        "added to reach the final price.",
    )
    final_price_unlock_prices = fields.Boolean(
        string="Salespeople Edit Prices and Discounts",
        config_parameter=UNLOCK_PARAM,
        help="By default only Sales Administrators can edit the unit price "
        "and the discounts of a line, the others set the final price. Tick to "
        "let every salesperson edit them.",
    )
