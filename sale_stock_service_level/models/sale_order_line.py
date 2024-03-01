# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    service_level_id = fields.Many2one(
        comodel_name="stock.service.level",
        string="Service level",
        related="order_id.service_level_id",
        help="The service level.",
    )

    def _prepare_procurement_values(self, group_id=False):
        return {
            **super()._prepare_procurement_values(group_id=group_id),
            "service_level_id": self.service_level_id.id,
        }
