from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        self._check_related_moves()
        return res

    def _check_related_moves(self):
        if self.env.context.get("skip_check_lot_selection_qty", False):
            return True
        for line in self.order_line:
            if line.lot_id:
                line.assign_move_with_lots()
        return True
