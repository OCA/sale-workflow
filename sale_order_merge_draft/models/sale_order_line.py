# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _merge_line_key(self):
        """Return the values two lines must have in common to be consolidated.

        Lines of the merged orders sharing this key become a single line whose
        quantity is the sum of theirs. Add an element to keep lines apart on one
        more field::

            def _merge_line_key(self):
                return super()._merge_line_key() + (self.return_date,)

        Add ``self.id`` to keep the lines from ever being consolidated, so that
        they are all moved over as they are. The values are compared with ``==``.
        """
        self.ensure_one()
        return (
            self.product_id.id,
            self.product_uom_id.id,
            self.price_unit,
            self.discount,
            self.analytic_distribution,
        )

    def _merge_sale_line(self, line):
        """Absorb the quantity of ``line`` into ``self``."""
        self.ensure_one()
        self.product_uom_qty += line.product_uom_qty

    def _move_to_order(self, order, sequence):
        """Reassign ``self`` to ``order``, after its existing lines."""
        self.ensure_one()
        self.write({"order_id": order.id, "sequence": sequence})
