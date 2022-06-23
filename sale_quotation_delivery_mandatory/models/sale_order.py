# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_confirm(self):
        for so in self:
            if not so.delivery_set:
                message = _(
                    "You have to specify a delivery method to confirm your quotation"
                )
                raise exceptions.ValidationError(message)
        return super().action_confirm()
