# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import float_compare, float_is_zero, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _convert_packaging_qty(self, qty, uom, packaging):
        """
        Convert the given qty with given UoM to the packaging uom.
        To do that, first transform the qty to the reference UoM and then
        transform using the packaging UoM.
        The given qty is not updated if the product has sell_only_by_packaging
        set to False or if the packaging is not set.
        Inspired from sale_stock/models.sale_order.py _check_package(...)
        :param qty: float
        :return: float
        """
        if not self or not packaging:
            return qty
        self.ensure_one()
        if self.sell_only_by_packaging and packaging.force_sale_qty:
            q = self.uom_id._compute_quantity(packaging.qty, uom)
            if (
                qty
                and q
                and float_compare(
                    qty / q,
                    float_round(qty / q, precision_rounding=1.0),
                    precision_rounding=0.001,
                )
                != 0
            ):
                qty = qty - (qty % q) + q
        return qty

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
