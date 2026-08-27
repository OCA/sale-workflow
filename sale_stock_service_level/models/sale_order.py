# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    service_level_id = fields.Many2one(
        string="Service level",
        index="btree_not_null",
        comodel_name="stock.service.level",
        help="The service level.",
    )
