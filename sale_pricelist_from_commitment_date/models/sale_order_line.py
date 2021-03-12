# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        return super(
            SaleOrderLine,
            self.with_context(force_pricelist_date=self.order_id.commitment_date),
        ).product_id_change()

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        return super(
            SaleOrderLine,
            self.with_context(force_pricelist_date=self.order_id.commitment_date),
        ).product_uom_change()

    @api.onchange(
        "product_id", "price_unit", "product_uom", "product_uom_qty", "tax_id"
    )
    def _onchange_discount(self):
        return super(
            SaleOrderLine,
            self.with_context(force_pricelist_date=self.order_id.commitment_date),
        )._onchange_discount()
