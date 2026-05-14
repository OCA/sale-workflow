# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.tools.float_utils import float_compare, float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _confirmation_error_message_sale_order_lot_selection(self):
        for line in self.order_line.filtered(lambda x: x.lot_id):
            if line.product_tracking != "serial" or float_is_zero(
                line.product_uom_qty, precision_rounding=line.product_uom.rounding
            ):
                continue
            product = line.product_id
            lot = line.lot_id
            free_qty = product._compute_quantities_dict(
                lot_id=lot.id, owner_id=False, package_id=False
            )[product.id]["free_qty"]
            if (
                float_compare(
                    free_qty,
                    line.product_uom_qty,
                    precision_rounding=line.product_uom.rounding,
                )
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
