# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import float_is_zero


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_first_packaging_with_multiple_qty(self, qty):
        """ Return multiple of product packaging for one quantity if exist.
        """
        self.ensure_one()
        packagings = self._get_packagings_with_multiple_qty(qty)
        return fields.first(packagings.sorted("qty", reverse=True))

    def _get_packagings_with_multiple_qty(self, qty):
        self.ensure_one()
        return self.packaging_ids.filtered(
            lambda pack: pack.can_be_sold
            and not float_is_zero(
                pack.qty, precision_rounding=pack.product_uom_id.rounding
            )
            and float_is_zero(
                qty % pack.qty, precision_rounding=pack.product_uom_id.rounding
            )
        )
