# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    min_sellable_qty = fields.Float(
        compute="_compute_variant_min_sellable_qty",
        help=(
            "Minimum sellable quantity, according to the available packagings, "
            "if Only Sell by Packaging is set."
        ),
    )

    @api.depends(
        "sell_only_by_packaging",
        "packaging_ids.qty",
        "packaging_ids.sales",
    )
    def _compute_variant_min_sellable_qty(self):
        for record in self:
            record.min_sellable_qty = 0.0
            if record.sell_only_by_packaging and record.packaging_ids:
                sellable_pkgs = record.packaging_ids.filtered(lambda p: p.sales)
                record.min_sellable_qty = fields.first(
                    sellable_pkgs.sorted(lambda p: p.qty)
                ).qty

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
