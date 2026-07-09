# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import UserError


class SaleOderLine(models.Model):
    _inherit = "sale.order"

    price_below_semaphore = fields.Boolean(compute="_compute_price_below_semaphore")

    def _compute_price_below_semaphore(self):
        self.price_below_semaphore = False
        for record in self:
            record.price_below_semaphore = any(
                record.order_line.mapped("price_below_semaphore")
            )

    def action_confirm(self):
        if not self.env.user.has_group("sales_team.group_sale_manager") and any(
            so.price_below_semaphore for so in self
        ):
            lines_price_below_pricelist = self.order_line.filtered(
                lambda line: line.price_below_semaphore
                and line._is_price_below_pricelist()
            )
            if lines_price_below_pricelist:
                raise UserError(
                    self.env._(
                        "There's a line with price below semaphore's accepted.\n\n"
                        "Please set the prices in a way that they are accepted by the "
                        "semaphore, or contact the purchasing administrators."
                    )
                )
        return super().action_confirm()
