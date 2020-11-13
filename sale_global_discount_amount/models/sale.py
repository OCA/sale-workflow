# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = ["sale.order", "discount.mixin"]
    _name = "sale.order"

    def _get_line_ids_by_model(self):
        line_ids = super()._get_line_ids_by_model()
        if self._name == "sale.order":
            line_ids = self.order_line
            return line_ids

    @api.model
    def create(self, vals):
        order = super().create(vals)
        if (
            "global_discount_amount" in vals
            and vals["global_discount_amount"] != 0.0
            and order.amount_untaxed != 0.0
            and not self.env.context.get("not_discount_lines_from_copy", False)
        ):
            self.env["sale.order.line"]._create_discount_lines(order=order)
        return order

    def write(self, vals):
        res = super().write(vals)
        if (
            "global_discount_amount" in vals
            or "order_line" in vals
            or not self.global_discount_ok
        ) and not self.env.context.get("discount_lines", False):
            self.order_line.filtered(lambda x: x.is_discount_line).with_context(
                discount_lines=True
            ).unlink()
            if self.global_discount_amount != 0.0:
                self.env["sale.order.line"]._create_discount_lines(order=self)
        return res

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        # for not create new discount lines
        self = self.with_context(not_discount_lines_from_copy=True)
        return super().copy(default=default)

    def _prepare_invoice(self):
        self.ensure_one()
        invoice_vals = super()._prepare_invoice()
        invoice_vals["global_discount_amount"] = self.global_discount_amount
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "discount.line.mixin"]
    _name = "sale.order.line"

    def _create_discount_lines(self, order):
        amount_untaxed = order.amount_untaxed
        # create discount lines by tax
        lines_with_price_tax = order.order_line.filtered(lambda x: x.price_tax != 0.0)
        res = {}
        for line in lines_with_price_tax:
            taxes = line.tax_id.compute_all(
                line.price_unit,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=order.partner_shipping_id,
            )["taxes"]
            for tax in line.tax_id:
                res.setdefault(tax, {"tax_amount": 0.0, "tax_base_amount": 0.0})
                for t in taxes:
                    if t["id"] == tax.id or t["id"] in tax.children_tax_ids.ids:
                        res[tax]["tax_amount"] += t["amount"]
                        res[tax]["tax_base_amount"] += t["base"]
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        for elem in res:
            tax_ids = [(6, 0, [elem[0].id])]
            tax_base_amount = elem[1]["tax_base_amount"]
            self._create_one_discount_line(
                order=order,
                tax_ids=tax_ids,
                tax_base_amount=tax_base_amount,
                amount_untaxed=amount_untaxed,
            )
        # create one discount line for the all order lines without price tax
        lines_without_price_tax = order.order_line.filtered(
            lambda x: x.price_tax == 0.0
        )
        without_tax_base_amount = 0.0
        for line in lines_without_price_tax:
            without_tax_base_amount += line.price_subtotal
        if lines_without_price_tax:
            tax_ids = [(6, 0, lines_without_price_tax.tax_id.ids)]
            self._create_one_discount_line(
                order=order,
                tax_ids=tax_ids,
                tax_base_amount=without_tax_base_amount,
                amount_untaxed=amount_untaxed,
            )

    def _create_one_discount_line(
        self, order, tax_ids, tax_base_amount, amount_untaxed
    ):
        global_discount_amount = order.global_discount_amount
        discount_product = self.env.ref(
            "account_global_discount_amount.discount_product"
        )
        discount_line = self.create(
            {
                "product_id": discount_product.id,
                "order_id": order.id,
                "product_uom_qty": 1,
            }
        )
        discount_line.product_id_change()
        price_unit = discount_line._prepare_discount_line_vals(
            amount_untaxed=amount_untaxed,
            tax_base_amount=tax_base_amount,
            global_discount_amount=global_discount_amount,
        )
        discount_line.write(
            {
                "price_unit": -1 * price_unit,
                "is_discount_line": True,
                "tax_id": tax_ids,
            }
        )

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        invoice_line_vals = super()._prepare_invoice_line(**optional_values)
        invoice_line_vals["is_discount_line"] = self.is_discount_line
        return invoice_line_vals
