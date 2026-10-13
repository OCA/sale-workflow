# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _price_compute(
        self, price_type, uom=None, currency=None, company=None, date=False
    ):
        if self.env.context.get("sol_lot"):
            lot = self.env.context.get("sol_lot")
            if price_type in ("standard_price", "list_price"):
                price = (
                    lot.lst_price if price_type == "list_price" else lot.standard_price
                )
                return dict.fromkeys(self.ids, price)
        return super()._price_compute(
            price_type,
            uom=uom,
            currency=currency,
            company=company,
            date=date,
        )
