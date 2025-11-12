# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _set_restrict_lot_id_from_sol(self, lot):
        """This method can be extended and/or used by other modules to intercept
        the change from the sales order line.
        """
        self.restrict_lot_id = lot
        self._do_unreserve()
        self.filtered(
            lambda move: move.state in ("confirmed', 'partially_available")
        )._action_assign()
