# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    min_sellable_qty = fields.Float(
        related="product_tmpl_id.min_sellable_qty",
        help=(
            "Minimum sellable quantity, expressed in the product unit, according "
            "to the available packaging units, if Only Sell by Packaging is set."
        ),
    )

    def _get_min_sellable_uom(self):
        """Return the smallest packaging unit this variant can be sold by.

        Packaging units are held by the template in 19.0, so the answer is the
        same for every variant of a given product.

        :return: a ``uom.uom`` recordset, possibly empty.
        """
        self.ensure_one()
        return self.product_tmpl_id._get_min_sellable_uom()

    def _convert_packaging_qty(self, qty, uom):
        """Round the given qty up to a whole number of the given packaging unit.

        The given qty is not updated if the product has sell_only_by_packaging
        set to False, if the unit is not one of the product packaging units or
        if that unit does not force the sale quantity.

        :param qty: float, expressed in ``uom``
        :param uom: the ``uom.uom`` record the qty is expressed in
        :return: float
        """
        if not self or not uom:
            return qty
        self.ensure_one()
        if (
            self.sell_only_by_packaging
            and uom.force_sale_qty
            and uom in self.uom_ids
            and qty
        ):
            qty = float_round(qty, precision_rounding=1.0, rounding_method="UP")
        return qty
