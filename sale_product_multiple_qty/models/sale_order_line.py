# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _sale_multiple_uom_has_unit_reference(self):
        """Return whether both UoMs share ``Units`` as common reference.

        This is used to distinguish quantity-based UoMs from dimensional UoMs.

        When both the order line UoM and the sales multiple UoM share the
        ``uom.product_uom_unit`` reference, the sellable quantity in the order
        line UoM should remain an integer count of items or packs.

        Examples:
            - Pack of 5 and Pack of 100 -> True
            - Pack of 6 and Pack of 100 -> True
            - 400 g and 1 kg -> False
        """
        self.ensure_one()
        unit_uom = self.env.ref("uom.product_uom_unit", raise_if_not_found=False)
        if not unit_uom:
            return False
        multiple_uom = self.product_id.sale_multiple_uom_id
        return self.product_uom_id._has_common_reference(
            unit_uom
        ) and multiple_uom._has_common_reference(unit_uom)

    def _get_sale_multiple_step_qty(self) -> float:
        """Return the effective quantity step in the order line UoM.

        The sales multiple is stored as a UoM on the product. This method
        expresses one unit of that sales multiple UoM in the order line UoM.

        For UoMs sharing ``Units`` as common reference, the result is rounded
        up to keep an integer count of items or packs.

        Examples:
            - sales multiple UoM: Pack of 100
              order line UoM: Pack of 5
              step quantity: 20

            - sales multiple UoM: Pack of 100
              order line UoM: Pack of 6
              raw step: 16.666...
              effective step quantity: 17

            - sales multiple UoM: 1 kg
              order line UoM: 400 g
              step quantity: 2.5
        """
        self.ensure_one()
        multiple_uom = self.product_id.sale_multiple_uom_id
        step_qty = multiple_uom._compute_quantity(1.0, self.product_uom_id, round=False)
        if self._sale_multiple_uom_has_unit_reference():
            step_qty = fields.Float.round(
                step_qty, precision_rounding=1.0, rounding_method="UP"
            )
        return step_qty

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

        For example (compatible UoMs: 100 is not divisible by 6):
            - order line UoM: Pack of 6 (6 units)
            - sales multiple UoM: Pack of 100 (100 units)
            - qty_to_order = 13 packs are rounded to 16.67 packs (100.02 units):
                13 packs of 6 units = 78 units -> 1.0 pack of 100 = 100 units
                -> 16.6667 packs of 6 units => rounded up to 17

        For example (dimensional UoMs: 1 kg is not divisible by 400g):
            - order line UoM: 400g (0.4 kg)
            - sales multiple UoM: 1 kg
            - qty_to_order = 2 packs are rounded to 2.5 packs (1 kg):
                2 packs of 400g = 0.8 kg -> 1.0 pack of 1 kg = 1 kg
                -> 2.5 packs of 400g = 1 kg (fractional, must NOT be rounded up to 3)
        """
        self.ensure_one()
        multiple_uom = self.product_id.sale_multiple_uom_id
        # For UoMs sharing ``Units`` as common reference, keep quantities that
        # are already multiples of the effective step unchanged.
        if self._sale_multiple_uom_has_unit_reference():
            step_qty = self._get_sale_multiple_step_qty()
            multiple = qty_to_order / step_qty
            rounded_multiple = fields.Float.round(
                multiple, precision_digits=0, rounding_method="UP"
            )
            if multiple_uom.compare(rounded_multiple, multiple) == 0:
                return qty_to_order

        packs = self.product_uom_id._compute_quantity(
            qty_to_order, multiple_uom, round=False
        )
        packs = fields.Float.round(packs, precision_digits=0, rounding_method="UP")
        qty_rounded = multiple_uom._compute_quantity(
            packs, self.product_uom_id, round=False
        )
        # For UoMs sharing ``Units`` as common reference,
        # round UP to keep an integer count of items or packs.
        if self._sale_multiple_uom_has_unit_reference():
            qty_rounded = fields.Float.round(
                qty_rounded, precision_rounding=1.0, rounding_method="UP"
            )
        return qty_rounded

    @api.onchange("product_id", "product_uom_qty", "product_uom_id")
    def _onchange_product_uom_qty_round_multiple(self):
        """Round product_uom_qty to a multiple of the sales multiple UoM.

        If sales multiple UoM is set on the product, this onchange rounds
        the order line quantity to the nearest multiple of that UoM.

        The rounding is limited to the form onchange.
        We do not override ``_compute_product_uom_qty``, because the goal
        is to suggest a rounded quantity to users in the UI,
        while preserving explicit programmatic values.
        """
        for line in self:
            multiple_uom = line.product_id.sale_multiple_uom_id
            if not multiple_uom:
                continue

            qty_to_order = line.product_uom_qty or 0.0
            if (
                not line.product_uom_id
                or line.product_uom_id.compare(qty_to_order, 0.0) <= 0
            ):
                continue
            rounded_qty = line._round_sale_qty_to_multiple(qty_to_order)
            # ``uom.uom.compare`` returns -1, 0 or 1 depending on whether
            # ``rounded_qty`` is lower than, equal to, or greater than
            # ``qty_to_order`` (within UoM rounding precision).
            if line.product_uom_id.compare(rounded_qty, qty_to_order) != 0:
                line.product_uom_qty = rounded_qty
