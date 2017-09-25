# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from openerp import api, fields, models


class SaleOrderRecommendation(models.TransientModel):
    _name = "sale.order.recommendation"
    _description = "Recommended products for current sale order"

    order_id = fields.Many2one(
        "sale.order",
        "Sale Order",
        default=lambda self: self._default_order_id(),
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    months = fields.Float(
        default=6,
        required=True,
        help="Consider these months backwards to generate recommendations.",
    )
    line_ids = fields.One2many(
        "sale.order.recommendation.line",
        "wizard_id",
        "Products",
    )
    line_amount = fields.Integer(
        "Number of recommendations",
        default=15,
        required=True,
        help="The less, the faster they will be found.",
    )

    @api.model
    def _default_order_id(self):
        return self.env.context.get("active_id", False)

    @api.multi
    @api.onchange("order_id", "months", "line_amount")
    def _generate_recommendations(self):
        """Generate lines according to context sale order."""
        start = datetime.now() - timedelta(days=self.months * 30)
        start = fields.Datetime.to_string(start)
        order_lines = self.order_id.order_line
        existing_product_ids = set(order_lines.mapped("product_id").ids)
        self.line_ids = False
        # Search delivered products in previous months
        found_lines = self.env["sale.order.line"].read_group(
            [
                ("order_partner_id", "child_of",
                 self.order_id.partner_id.commercial_partner_id.id),
                ("order_id.date_order", ">=", start),
                "|", ("qty_delivered", "!=", 0.0),
                     ("order_id", "=", self.order_id.id),
            ],
            ["product_id", "qty_delivered"],
            ["product_id"],
            limit=self.line_amount,
            lazy=False,
        )
        # Manual ordering that circumvents ORM limitations
        found_lines = sorted(
            found_lines,
            key=lambda res: (
                res["product_id"][0] in existing_product_ids,
                res["__count"],
                res["qty_delivered"],
            ),
            reverse=True,
        )
        # Add those recommendations too
        for line in found_lines:
            new_line = self.env["sale.order.recommendation.line"].new({
                "product_id": line["product_id"][0],
                "times_delivered": line["__count"],
                "units_delivered": line["qty_delivered"],
            })
            if new_line.product_id.id in existing_product_ids:
                new_line.units_included = (
                    order_lines
                    .filtered(lambda r: r.product_id == new_line.product_id)
                    .product_uom_qty)
            self.line_ids += new_line

    @api.multi
    def action_accept(self):
        """Propagate recommendations to sale order."""
        so_lines = self.env["sale.order.line"]
        existing_products = self.order_id.mapped("order_line.product_id")
        for wiz_line in self.line_ids:
            # Use preexisting line if any
            if wiz_line.product_id <= existing_products:
                so_line = self.order_id.order_line.filtered(
                    lambda r: r.product_id == wiz_line.product_id)
                # Merge multiple if needed
                if len(so_line) > 1:
                    so_line[0].product_uom_qty += sum(
                        so_line[1:].mapped("product_uom_qty"))
                    so_line[1:].unlink()
            # Use a new in-memory line otherwise
            else:
                so_line = so_lines.new({
                    "order_id": self.order_id.id,
                })
            # Delete if needed
            if not wiz_line.units_included:
                so_line.unlink()
                continue
            # Apply changes
            so_line.update({
                "name": wiz_line.product_id.display_name,
                "product_id": wiz_line.product_id.id,
                "product_uom_qty": wiz_line.units_included,
                "product_uom": wiz_line.product_id.uom_id.id,
            })
            so_line.product_id_change()
            so_line.product_uom_change()
            so_lines |= so_line
        self.order_id.order_line |= so_lines


class SaleOrderRecommendationLine(models.TransientModel):
    _name = "sale.order.recommendation.line"
    _description = "Recommended product for current sale order"
    _order = "id"

    currency_id = fields.Many2one(
        related="product_id.currency_id",
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="wizard_id.order_id.partner_id",
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        readonly=True,
    )
    price_unit = fields.Monetary(
        compute="_compute_price_unit",
    )
    pricelist_id = fields.Many2one(
        related="wizard_id.order_id.pricelist_id",
        readonly=True,
    )
    times_delivered = fields.Integer(
        readonly=True,
    )
    units_delivered = fields.Float(
        readonly=True,
    )
    units_included = fields.Float()
    wizard_id = fields.Many2one(
        "sale.order.recommendation",
        "Wizard",
        ondelete="cascade",
        required=True,
        readonly=True,
    )

    @api.multi
    @api.depends("partner_id", "product_id", "pricelist_id", "units_included")
    def _compute_price_unit(self):
        for one in self:
            one.price_unit = one.product_id.with_context(
                partner=one.partner_id.id,
                pricelist=one.pricelist_id.id,
                quantity=one.units_included,
            ).price
