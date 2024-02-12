# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_tax_id(self):
        super(SaleOrderLine, self)._compute_tax_id()
        map_tax = self.env["account.tax"]._map_exclude_tax()
        for line in self:
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(
                lambda r: not line.company_id or r.company_id == line.company_id
            )
            if not line.order_id.pricelist_id.price_include_taxes:
                # pricelist not include tax
                taxes = self.env["account.tax"]._get_substitute_taxes(
                    self, taxes, map_tax
                )
            fpos = (
                line.order_id.fiscal_position_id
                or line.order_id.partner_id.property_account_position_id
            )
            line.tax_id = (
                fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id)
                if fpos
                else taxes
            )

    @api.onchange("product_id")
    def product_id_change(self):
        self._upd_onchange_ctx()
        return super(SaleOrderLine, self).product_id_change()

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        self._upd_onchange_ctx()
        return super(SaleOrderLine, self).product_uom_change()

    def _upd_onchange_ctx(self):
        """Only to add 'pricelist' context"""
        ctx = self.env.context.copy()
        ctx.update(dict(pricelist=self.order_id.pricelist_id.id))
        self.env.context = ctx
        # with_context() doesn't work here (loosing product_id record),
        # then directly update context


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def update_prices(self):
        for record in self:
            record.order_line._compute_tax_id()
            super(
                SaleOrder, record.with_context(pricelist=record.pricelist_id.id)
            ).update_prices()
