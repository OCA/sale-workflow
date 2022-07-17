# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import threading

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def update_prices(self):
        for record in self:
            record.order_line._compute_tax_id()
            super(
                SaleOrder, record.with_context(pricelist=record.pricelist_id.id)
            ).update_prices()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_tax_id(self):
        for line in self:
            line = line.with_context(
                price_include_taxes=line.order_id.pricelist_id.price_include_taxes
            )
            super(SaleOrderLine, line)._compute_tax_id()
            if getattr(
                threading.currentThread(), "testing", False
            ) and not self._context.get("test_pricelist_tax"):
                continue
            pricelist = line.order_id.pricelist_id
            if not pricelist.price_include_taxes and any(
                line.tax_id.mapped("price_include")
            ):
                raise UserError(
                    _(
                        "Tax with include price with pricelist b2b '%s' "
                        "is not supported" % pricelist.name
                    )
                )

    @api.onchange("product_id")
    def product_id_change(self):
        self = self.with_context(pricelist=self.order_id.pricelist_id.id)
        return super().product_id_change()

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        self = self.with_context(pricelist=self.order_id.pricelist_id.id)
        return super().product_uom_change()
