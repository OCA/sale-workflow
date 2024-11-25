# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    used_for_sale_reservation = fields.Boolean(default=False)

    @api.constrains("used_for_sale_reservation", "quantity_done")
    def _check_used_for_sale_reservation(self):
        for move in self:
            if move.used_for_sale_reservation and move.quantity_done:
                raise ValidationError(
                    _(
                        "You cannot set a quantity done on a move used for sale reservation"
                    )
                )

    def _action_assign(self, force_qty=None):
        new_self = self.filtered(lambda m: not m.used_for_sale_reservation)
        return super(StockMove, new_self)._action_assign(force_qty=force_qty)
