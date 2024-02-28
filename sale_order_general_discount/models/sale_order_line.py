# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id", "order_id.general_discount")
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            # We check the value of general_discount on origin too to cover
            # the case where a discount was set to a value != 0 and then
            # set again to 0 to remove the discount on all the lines at the same
            # time
            if line.order_id.general_discount or line.order_id._origin.general_discount:
                line.discount = line.order_id.general_discount
        return res
