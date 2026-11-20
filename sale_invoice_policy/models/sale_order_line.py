# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.fields import Domain


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _order_invoice_policy_applies(self) -> bool:
        """Goods follow the order policy; services, sections and combos follow core."""
        self.ensure_one()
        order_policy = self.order_id.invoice_policy
        product = self.product_id
        if order_policy not in ("order", "delivery"):
            return False
        if self.display_type or not product:
            return False
        return product.type not in ("service", "combo")

    @api.depends("order_id.invoice_policy", "product_id.type", "display_type")
    def _compute_invoice_policy(self) -> None:
        result = super()._compute_invoice_policy()
        for line in self:
            if line._order_invoice_policy_applies():
                line.invoice_policy = line.order_id.invoice_policy
        return result

    def _search_invoice_policy(self, operator, value) -> Domain:
        core_domain = super()._search_invoice_policy(operator, value)
        overridden = Domain(
            [
                ("display_type", "=", False),
                ("product_id", "!=", False),
                ("product_id.type", "not in", ("service", "combo")),
                ("order_id.invoice_policy", "in", ("order", "delivery")),
            ]
        )
        effective = overridden & Domain("order_id.invoice_policy", operator, value)
        return (core_domain & ~overridden) | effective

    @api.depends(
        "qty_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "state",
        "order_id.invoice_overages",
        "invoice_policy",
        "order_id.invoice_policy",
    )
    def _compute_qty_to_invoice(self):
        return super()._compute_qty_to_invoice()

    @api.depends(
        "state",
        "product_id",
        "untaxed_amount_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "price_unit",
        "invoice_policy",
        "order_id.invoice_policy",
    )
    def _compute_untaxed_amount_to_invoice(self):
        """Core amounts follow the product policy; goods use the order policy."""
        result = super()._compute_untaxed_amount_to_invoice()
        for line in self:
            if line.state != "sale" or not line._order_invoice_policy_applies():
                continue
            if line.invoice_policy == line.product_id.invoice_policy:
                continue
            quantity = (
                line.qty_delivered
                if line.invoice_policy == "delivery"
                else line.product_uom_qty
            )
            price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_subtotal = price_reduce * quantity
            included_tax = False
            for tax in line.tax_ids:
                if tax.price_include:
                    included_tax = True
            if included_tax:
                price_subtotal = line.tax_ids.compute_all(
                    price_reduce,
                    currency=line.currency_id,
                    quantity=quantity,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )["total_excluded"]
            line.untaxed_amount_to_invoice = (
                price_subtotal - line.untaxed_amount_invoiced
            )
        return result
