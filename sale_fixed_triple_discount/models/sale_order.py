# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    show_discount_warning_label = fields.Boolean(
        compute="_compute_show_discount_warning_label"
    )

    @api.depends(
        "order_line.discount_fixed",
        "order_line.discount1",
        "order_line.discount2",
        "order_line.discount3",
    )
    def _compute_show_discount_warning_label(self):
        for sale in self:
            sale.show_discount_warning_label = any(
                line.discount_fixed
                and (line.discount1 or line.discount2 or line.discount3)
                for line in sale.order_line
            )
