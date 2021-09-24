# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    route_id = fields.Many2one(
        readonly=True,
    )
