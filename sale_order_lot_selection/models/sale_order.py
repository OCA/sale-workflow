# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _confirmation_error_message_sale_order_lot_selection(self):
        for lot in self.order_line.lot_id:
            # We check the quantities for all lines that use the same lot to ensure
            # that we do not confirm orders that use the same lot across multiple lines
            lines = self.order_line.filtered(lambda x, lot=lot: x.lot_id == lot)
            line_0 = fields.first(lines)
            if line_0.product_tracking != "serial":
                continue
            product = line_0.product_id
            product_uom = product.uom_id
            qty = sum(
                line.product_uom._compute_quantity(
                    line.product_uom_qty, product_uom, round=False
                )
                for line in lines
            )
            if float_is_zero(qty, precision_rounding=product_uom.rounding):
                continue
            free_qty = product._compute_quantities_dict(
                lot_id=lot.id, owner_id=False, package_id=False
            )[product.id]["free_qty"]
            if (
                float_compare(free_qty, qty, precision_rounding=product_uom.rounding)
                < 0
            ):
                return _("The serial number %(serial)s is not available") % {
                    "serial": lot.display_name,
                }
        return False

    def _confirmation_error_message(self):
        res = super()._confirmation_error_message()
        msg_lot_selection = self._confirmation_error_message_sale_order_lot_selection()
        if msg_lot_selection:
            return msg_lot_selection
        return res
