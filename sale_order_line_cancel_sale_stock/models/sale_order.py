# Copyright 2023 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_cancel(self):
        new_self = self.with_context(ignore_sale_order_line_cancel=True)
        res = super(SaleOrder, new_self)._action_cancel()
        return res
