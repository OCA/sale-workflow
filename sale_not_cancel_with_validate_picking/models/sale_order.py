# Copyright 2021 Daniel Domínguez - https://xtendoo.es
# Copyright 2021 Manuel Calero - https://xtendoo.es
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        res = super().action_cancel()
        picking_ids = self.picking_ids.filtered(lambda x: x.state == "done")
        if picking_ids:
            raise UserError(
                _(
                    "You cannot cancel an order with validated deliveries, "
                    "you must first cancel "
                )
                + ", ".join(picking_ids.mapped("name"))
            )
        return res
