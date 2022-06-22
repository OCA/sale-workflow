# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BlanketOrderLine(models.Model):
    _inherit = "sale.blanket.order.line"

    margin = fields.Float(
        compute="_compute_margin",
        digits="Product Price",
        store=True,
        groups="base.group_user",
    )
    margin_percent = fields.Float(
        "Margin (%)",
        compute="_compute_margin",
        store=True,
        group_operator="avg",
        groups="base.group_user",
    )
    purchase_price = fields.Float(
        "Cost",
        compute="_compute_purchase_price",
        digits="Product Price",
        store=True,
        readonly=False,
        groups="base.group_user",
    )

    @api.depends("product_id", "company_id", "currency_id", "original_uom_qty")
    def _compute_purchase_price(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            product_cost = line.product_id.standard_price
            line.purchase_price = line._convert_price(
                product_cost, line.product_id.uom_id
            )

    @api.depends("price_subtotal", "original_uom_qty", "purchase_price", "price_unit")
    def _compute_margin(self):
        for line in self:
            line.margin = line.price_subtotal - (
                line.purchase_price * line.original_uom_qty
            )
            line.margin_percent = (
                line.price_subtotal and line.margin / line.price_subtotal
            )

    def _convert_price(self, product_cost, from_uom):
        self.ensure_one()
        if not product_cost:
            # If the standard_price is 0
            # Avoid unnecessary computations
            # and currency conversions
            if not self.purchase_price:
                return product_cost
        from_currency = self.product_id.cost_currency_id
        to_cur = self.currency_id or self.order_id.currency_id
        to_uom = self.product_uom
        if to_uom and to_uom != from_uom:
            product_cost = from_uom._compute_price(
                product_cost,
                to_uom,
            )
        if self.date_schedule and self.date_schedule <= fields.Date.today():
            date = self.date_shedule
        else:
            date = fields.Date.today()
        return (
            from_currency._convert(
                from_amount=product_cost,
                to_currency=to_cur,
                company=self.company_id or self.env.company,
                date=date,
                round=False,
            )
            if to_cur and product_cost
            else product_cost
        )
        # The pricelist may not have been set, therefore no conversion
        # is needed because we don't know the target currency..
