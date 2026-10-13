# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools.misc import formatLang


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _round_sale_qty_to_multiple(self, qty_to_order: float) -> float:
        """Round the order line quantity to a multiple of the sales multiple UoM.

        :param qty_to_order: quantity expressed in the order line UoM (product_uom_id).
        :return: rounded quantity expressed in the order line UoM (product_uom_id).

        This method is inspired by
        ``stock.warehouse.orderpoint::_get_multiple_rounded_qty``.
        Round using "UP" strategy to the nearest multiple of
        product_id.sale_multiple_uom_id:

            - Convert qty_to_order from the product_uom_id to the
            product_id.sale_multiple_uom_id
            - Round the quantity using "UP" strategy
            - Convert back to the product_uom_id quantity

        Being said, for the UoMs which share common reference unit (e.g. Units)
        the sales multiple UoM is divisible by the order line UoM
        and the division result is usually an integer.
        But for dimensional UoMs like (e.g. Kg(s), Meter(s)) the rounding result
        can be a floating point number which is perfectly acceptable.

        For example (compatible UoMs: 100 is divisible by 5):
            - order line UoM: Pack of 5 (5 units)
            - sales multiple UoM: Pack of 100 (100 units)
            - qty_to_order = 15 packs are rounded to 20 packs (100 units):
                15 packs of 5 units = 75 units
                -> 1 pack of 100 = 100 units -> 20 packs of 5 units
            - qty_to_order = 55 packs are rounded to 60 packs (300 units):
                55 packs of 5 units = 275 units
                -> 3 packs of 100 = 300 units -> 60 packs of 5 units

        For example (fractional result: 100 is not divisible by 6):
            - order line UoM: Pack of 6 (6 units)
            - sales multiple UoM: Pack of 100 (100 units)
            - qty_to_order = 13 packs are rounded to 16.67 packs (100.02 units):
                13 packs of 6 units = 78 units -> 1.0 pack of 100 = 100 units
                -> 16.6667 packs of 6 units
        """
        self.ensure_one()
        # This method is called in constraint to get the rounded quantity for the check.
        # But, the ``line.product_uom_qty`` at that stage is already rounded.
        # We need to be sure we don't round "UP" already multiple quantity.
        multiple_uom = self.product_id.sale_multiple_uom_id
        packs = self.product_uom_id._compute_quantity(
            qty_to_order, multiple_uom, rounding_method="HALF-EVEN"
        )
        packs_up = fields.Float.round(packs, precision_digits=0, rounding_method="UP")
        enough_packs = float_compare(
            packs, packs_up, precision_rounding=multiple_uom.rounding
        )
        if enough_packs == 0:
            return qty_to_order
        qty_rounded = multiple_uom._compute_quantity(packs_up, self.product_uom_id)
        return qty_rounded

    @api.onchange("product_id", "product_uom_qty", "product_uom_id")
    def _onchange_product_uom_qty_round_multiple(self):
        """Round product_uom_qty to a multiple of the sales multiple UoM.

        If sales multiple UoM is set on the product, this onchange rounds
        the order line quantity to the nearest multiple of that UoM.
        """
        for line in self:
            multiple_uom = line.product_id.sale_multiple_uom_id
            if not multiple_uom:
                continue

            qty_to_order = line.product_uom_qty or 0.0
            if qty_to_order <= 0:
                continue
            rounded_qty = line._round_sale_qty_to_multiple(qty_to_order)
            # ``uom.uom::compare`` return -1, 0 or 1, if ``rounded_qty``
            # is lower than, equal to, or greater than ``qty_to_order``
            qty_diff = line.product_uom_id.compare(rounded_qty, qty_to_order)
            if qty_diff != 0:
                line.product_uom_qty = rounded_qty

    @api.constrains(
        "product_id",
        "product_uom_qty",
        "product_uom_id",
    )
    def _check_rounded_sale_multiple_qty(self):
        """Ensure product_uom_qty is a multiple of the sales multiple UoM."""
        for line in self:
            multiple_uom = line.product_id.sale_multiple_uom_id
            if not multiple_uom:
                continue

            qty_to_order = line.product_uom_qty or 0.0
            if qty_to_order <= 0:
                continue
            # This constraint is declared to prevent line wrong update
            # outside of the form, directly by ``write``.
            # Onchange wasn't played in such case,
            # so qty_to_order is not rounded.
            #
            # The line.product_id with such configuration:
            #   order line UoM: Pack of 6 (5 units)
            #   sales multiple UoM: Pack of 100 (100 units)
            #   qty_to_order = 13 packs
            #   rounded_qty = 16.67 packs
            #
            # qty_diff = line.product_uom_id.compare(16.67, 13) => 1
            precision = self.env["decimal.precision"].precision_get("Product Unit")
            rounded_qty = line._round_sale_qty_to_multiple(qty_to_order)
            qty_diff = line.product_uom_id.compare(rounded_qty, qty_to_order)
            format_qty = formatLang(self.env, rounded_qty, digits=precision)
            if qty_diff != 0:
                msg = self.env._(
                    "The rounded qty '%(rounded_qty)s' is not valid "
                    "considering order line UoM '%(uom)s'.\n"
                    "It should be a multiple of '%(multiple)s'.\n",
                    rounded_qty=format_qty,
                    uom=line.product_uom_id.display_name,
                    multiple=multiple_uom.display_name,
                )
                raise ValidationError(msg)
