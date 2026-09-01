# © 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import threading

from odoo import api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = "sale.order"
    _description = "Sales Order"
    _inherit = ["sale.order", "price.include.tax.mixin"]

    def action_update_prices(self):  # pylint: disable=missing-return
        for record in self:
            record.order_line._compute_tax_id()
            super(
                SaleOrder, record.with_context(pricelist=record.pricelist_id.id)
            ).action_update_prices()

    @api.depends("order_line", "order_line.tax_id", "order_line.tax_id.price_include")
    def _compute_price_tax_state(self):
        return super()._compute_price_tax_state()

    def action_confirm(self):
        for rec in self:
            if rec.price_tax_state == "exception":
                raise UserError(
                    self.env._(
                        "Sale Order lines must have the same kind of taxes "
                        "(price include or exclude)."
                    )
                )
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_tax_id(self):  # pylint: disable=missing-return
        for line in self:
            line = line.with_context(
                price_include_taxes=line.order_id.pricelist_id.price_include_taxes
            )
            super(SaleOrderLine, line)._compute_tax_id()

            if getattr(
                threading.current_thread(), "testing", False
            ) and not self._context.get("test_pricelist_tax"):
                continue

            pricelist = line.order_id.pricelist_id

            if not pricelist.price_include_taxes and any(
                line.tax_id.mapped("price_include")
            ):
                raise UserError(
                    self.env._(
                        "Tax with include price with pricelist b2b '%s' "
                        "is not supported",
                        pricelist.name,
                    )
                )

    def _compute_price_unit(self):  # pylint: disable=missing-return
        self = self.with_context(pricelist=self.order_id.pricelist_id.id)
        super()._compute_price_unit()
