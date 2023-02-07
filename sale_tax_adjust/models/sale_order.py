# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tax_totals_json = fields.Char(
        readonly=False, help="Edit Tax amounts if you encounter rounding issues."
    )

    @api.depends(
        "order_line.tax_id",
        "order_line.price_subtotal",
        "amount_total",
        "amount_untaxed",
    )
    def _compute_tax_totals_json(self):
        """Allow user can edit taxes amounts"""
        res = super()._compute_tax_totals_json()
        for order in self:
            tax_totals = json.loads(order.tax_totals_json)
            tax_totals["allow_tax_edition"] = order.state == "draft"
            for amount_by_group_list in tax_totals["groups_by_subtotal"].values():
                for amount_by_group in amount_by_group_list:
                    tax_lines = order.order_line.filtered(
                        lambda line: amount_by_group["tax_group_id"]
                        in line.tax_id.mapped("tax_group_id").ids
                    )
                    tax_group_amount = sum(tax_lines.mapped("price_tax"))
                    # Update value taxes if edit tax amounts
                    if (
                        tax_group_amount
                        and amount_by_group["tax_group_amount"] != tax_group_amount
                    ):
                        amount_by_group["tax_group_amount"] = tax_group_amount
                        amount_by_group["formatted_tax_group_amount"] = (
                            formatLang(
                                self.env,
                                tax_group_amount,
                                currency_obj=order.currency_id,
                            ),
                        )
            order.tax_totals_json = json.dumps(tax_totals)
        return res

    @api.onchange("tax_totals_json")
    def _onchange_tax_totals_json(self):
        """This method is triggered by the tax group widget. It allows modifying the right
        order lines depending on the tax group whose amount got edited."""
        for order in self:
            if not order.currency_id:
                continue
            tax_totals = json.loads(order.tax_totals_json)
            for amount_by_group_list in tax_totals["groups_by_subtotal"].values():
                for amount_by_group in amount_by_group_list:
                    tax_lines = order.order_line.filtered(
                        lambda line: amount_by_group["tax_group_id"]
                        in line.tax_id.mapped("tax_group_id").ids
                    )
                    if tax_lines:
                        tax_group_old_amount = sum(tax_lines.mapped("price_tax"))
                        delta_amount = (
                            tax_group_old_amount - amount_by_group["tax_group_amount"]
                        )
                        if not order.currency_id.is_zero(delta_amount):
                            # It will not trigger, if price tax is zero amount.
                            # so, we loop line for split update price tax in line
                            count_line = len(tax_lines)
                            for i, tax_line in enumerate(tax_lines):
                                tax_line.tax_adjust = True
                                # For result line tax is not zero or negative,
                                if (
                                    float_compare(tax_line.price_tax, delta_amount, 2)
                                    == 1
                                ):
                                    tax_line.price_tax = (
                                        tax_line.price_tax - delta_amount
                                    )
                                    break
                                delta_amount = (
                                    abs(tax_line.price_tax - delta_amount) + 1
                                )
                                tax_line.price_tax = 1
                                # Not allow adjust tax less than count line.
                                if i == count_line - 1 and delta_amount > 0.0:
                                    raise UserError(
                                        _(
                                            "You can not adjust tax less than {}."
                                        ).format(count_line)
                                    )
            # Trigger new calculation of tax totals
            order._compute_tax_totals_json()

    def action_refresh_taxes(self):
        for rec in self:
            # NOTE: It will overwrite with line adjust only
            rec.order_line.write({"tax_adjust": False})
            rec.order_line._compute_amount()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    tax_adjust = fields.Boolean(
        copy=False,
        help="trigger line with adjust tax",
    )

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_id")
    def _compute_amount(self):
        res = False
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            # taxes = line.tax_id.compute_all(**line._prepare_compute_all_values())
            price_tax = sum(t.get("amount", 0.0) for t in taxes.get("taxes", []))
            # it will not update tax, if tax adjust and tax compute is not equal.
            if line.tax_adjust and line.price_tax and line.price_tax != price_tax:
                line.update(
                    {
                        "price_total": taxes["total_included"],
                        "price_subtotal": taxes["total_excluded"],
                    }
                )
                continue
            res = super(SaleOrderLine, line)._compute_amount()
        return res

    @api.onchange(
        "product_uom_qty", "discount", "price_unit", "price_subtotal", "tax_id"
    )
    def _onchange_line_without_tax(self):
        """Auto refresh tax. if line sale is change"""
        self.order_id.action_refresh_taxes()
