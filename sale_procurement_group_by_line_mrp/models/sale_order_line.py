# Copyright 2026 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_qty_procurement(self, previous_product_uom_qty=False):
        """Fix double procurement on nested kit products.

        sale_mrp overrides _get_qty_procurement for kit products and ignores
        previous_product_uom_qty, using _compute_kit_quantities() instead.
        For nested kits, the inner kit's component moves don't match the outer
        kit's BoM, so it returns 0, causing super()._action_launch_stock_rule
        to run procurement a second time and double all stock moves.

        By checking previous_product_uom_qty first (only for kit products),
        we signal that procurement was already handled upstream, without
        affecting the default behavior for non-kit products.
        """
        self.ensure_one()
        if (
            previous_product_uom_qty
            and self.id in previous_product_uom_qty
            and self.env["mrp.bom"]._bom_find(
                product=self.product_id, bom_type="phantom"
            )
        ):
            return previous_product_uom_qty[self.id]
        return super()._get_qty_procurement(
            previous_product_uom_qty=previous_product_uom_qty
        )
