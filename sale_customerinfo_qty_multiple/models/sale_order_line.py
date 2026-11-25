# Copyright 2026 Aures Tic Consultors S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import math

from odoo import _, api, fields, models
from odoo.tools import float_compare, float_round

# How many multiples, from the exact number of them. Rounding to the nearest one:
# halves go up and anything ordered is at least one multiple
ROUNDING = {
    "down": math.floor,
    "up": math.ceil,
    "nearest": lambda times: max(math.floor(times + 0.5), 1 if times > 0 else 0),
}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    customer_qty_multiple = fields.Float(
        string="Customer Multiple",
        compute="_compute_customer_qty_multiple",
        digits="Product Unit of Measure",
        help="The customer buys this product in multiples of this quantity, "
        "in the unit of measure of the product.",
    )
    customer_qty_multiple_policy = fields.Selection(
        [
            ("down", "Round down"),
            ("up", "Round up"),
            ("nearest", "Round to the nearest"),
            ("warning", "Only warn"),
        ],
        compute="_compute_customer_qty_multiple",
    )
    is_not_customer_qty_multiple = fields.Boolean(
        compute="_compute_is_not_customer_qty_multiple",
    )

    @api.depends("product_id", "order_partner_id")
    def _compute_customer_qty_multiple(self):
        for line in self:
            customerinfo = self.env["product.customerinfo"]
            if line.product_id and line.order_partner_id:
                customerinfo = line.product_id._select_customerinfo(
                    partner=line.order_partner_id
                )
            line.customer_qty_multiple = customerinfo.sale_qty_multiple
            line.customer_qty_multiple_policy = (
                customerinfo.sale_qty_multiple_policy or False
            )

    @api.depends("product_uom_qty", "product_uom", "customer_qty_multiple")
    def _compute_is_not_customer_qty_multiple(self):
        for line in self:
            line.is_not_customer_qty_multiple = bool(
                line.customer_qty_multiple
                and line._customer_qty_multiple_round(line.product_uom_qty, "down")
                != line.product_uom_qty
            )

    def _customer_qty_multiple_round(self, qty, policy=None):
        """``qty`` (in the line's unit) rounded to the customer's multiple
        following ``policy`` (by default, the one of the customer info). Returns
        ``qty`` itself when there is nothing to round."""
        self.ensure_one()
        multiple = self.customer_qty_multiple
        policy = policy or self.customer_qty_multiple_policy
        if not multiple or policy not in ROUNDING or not self.product_id:
            return qty
        product_uom = self.product_id.uom_id
        line_uom = self.product_uom or product_uom
        product_qty = line_uom._compute_quantity(qty, product_uom, round=False)
        # avoid 2.9999999 multiples because of float precision
        times = float_round(product_qty / multiple, precision_digits=6)
        times = ROUNDING[policy](times)
        rounded = product_uom._compute_quantity(times * multiple, line_uom, round=False)
        precision = line_uom.rounding or 0.01
        if not float_compare(rounded, qty, precision_rounding=precision):
            return qty
        return rounded

    def _customer_qty_multiple_message(self, ordered, adjusted):
        self.ensure_one()
        return _(
            "%(product)s: the customer buys it in multiples of %(multiple)s "
            "%(uom)s; %(ordered)s ordered, %(adjusted)s set.",
            product=self.product_id.display_name,
            multiple=self.customer_qty_multiple,
            uom=self.product_id.uom_id.name,
            ordered=ordered,
            adjusted=adjusted,
        )

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        """When the product is chosen, start from the first valid quantity
        instead of rounding the default one (1 would become 0 when rounding
        down)."""
        res = super()._onchange_product_id_warning()
        for line in self:
            if (
                line.customer_qty_multiple_policy in ROUNDING
                and line.is_not_customer_qty_multiple
            ):
                line.product_uom_qty = line._customer_qty_multiple_round(
                    line.product_uom_qty, "up"
                )
        return res

    @api.onchange("product_uom_qty", "product_uom")
    def _onchange_customer_qty_multiple(self):
        if not self.customer_qty_multiple or not self.product_uom_qty:
            return
        if self.customer_qty_multiple_policy == "warning":
            if self.is_not_customer_qty_multiple:
                return {
                    "warning": {
                        "title": _("Quantity not a multiple"),
                        "message": _(
                            "%(product)s: the customer buys it in multiples of "
                            "%(multiple)s %(uom)s.",
                            product=self.product_id.display_name,
                            multiple=self.customer_qty_multiple,
                            uom=self.product_id.uom_id.name,
                        ),
                    }
                }
            return
        ordered = self.product_uom_qty
        adjusted = self._customer_qty_multiple_round(ordered)
        if adjusted == ordered:
            return
        self.product_uom_qty = adjusted
        return {
            "warning": {
                "title": _("Quantity adjusted"),
                "message": self._customer_qty_multiple_message(ordered, adjusted),
            }
        }

    def _customer_qty_multiple_apply(self):
        """Round the quantity of lines created or changed outside the form
        (imports, portals, EDI...) and leave a note on the order."""
        if self.env.context.get("skip_customer_qty_multiple"):
            return
        for line in self:
            if line.display_type or line.state not in ("draft", "sent"):
                continue
            ordered = line.product_uom_qty
            adjusted = line._customer_qty_multiple_round(ordered)
            if adjusted == ordered:
                continue
            line.with_context(
                skip_customer_qty_multiple=True
            ).product_uom_qty = adjusted
            line.order_id.message_post(
                body=line._customer_qty_multiple_message(ordered, adjusted)
            )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._customer_qty_multiple_apply()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if "product_uom_qty" in vals or "product_uom" in vals:
            self._customer_qty_multiple_apply()
        return res
