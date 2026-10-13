# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    discount_distribution = fields.Json(
        default=list,
        help="Ordered list of percentage discounts applied multiplicatively "
        "by this pricelist rule.",
    )

    # ``percent_price`` (Discount mode) and ``price_discount`` (Formula mode)
    # become mirrors of the multiplicative aggregation of
    # ``discount_distribution``. Keeping them as editable stored computed
    # fields lets core ``_compute_price`` work untouched, while a direct write
    # on either field is reflected back into the distribution through the
    # inverse, exactly like the sibling ``account_multi_discount`` module.
    # ``precompute`` makes the aggregation available already at ``create``
    # time, when the rule is saved with its distribution in a single call.
    percent_price = fields.Float(
        compute="_compute_percent_price",
        inverse="_inverse_percent_price",
        store=True,
        readonly=False,
        precompute=True,
    )
    # ``default=None`` drops the core ``default=0``: otherwise that default
    # would be injected into the ``create`` values, fire the inverse with a
    # zero discount and wipe the distribution before it is ever aggregated.
    price_discount = fields.Float(
        compute="_compute_price_discount",
        inverse="_inverse_price_discount",
        store=True,
        readonly=False,
        precompute=True,
        default=None,
    )

    @api.depends("discount_distribution")
    def _compute_percent_price(self):
        AccountMoveLine = self.env["account.move.line"]
        for item in self:
            item.percent_price = AccountMoveLine._aggregate_discount_distribution(
                item.discount_distribution
            )

    @api.depends("discount_distribution")
    def _compute_price_discount(self):
        AccountMoveLine = self.env["account.move.line"]
        for item in self:
            item.price_discount = AccountMoveLine._aggregate_discount_distribution(
                item.discount_distribution
            )

    def _inverse_percent_price(self):
        for item in self:
            item.discount_distribution = (
                [item.percent_price] if item.percent_price else []
            )

    def _inverse_price_discount(self):
        for item in self:
            item.discount_distribution = (
                [item.price_discount] if item.price_discount else []
            )
