# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            if (
                not line.discount
                and line.order_id.pricelist_id
                and line.pricelist_item_id
                and line.pricelist_item_id.show_surcharge
            ):
                pricelist_price = line._get_pricelist_price()
                base_price = line._get_pricelist_price_before_discount()

                if base_price != 0:  # Avoid division by zero
                    line.discount = (base_price - pricelist_price) / base_price * 100
        return res

    def _get_display_price(self):
        res = super()._get_display_price()
        if self.pricelist_item_id and self.pricelist_item_id.show_surcharge:
            return self._get_pricelist_price_before_discount()
        return res
