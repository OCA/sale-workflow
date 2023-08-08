# Copyright 2023 Moduon Team
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order = fields.Datetime(
        related="order_id.date_order",
        readonly=True,
        store=True,
        index=True,
    )
    account_analytic_id = fields.Many2one(
        related="order_id.analytic_account_id",
        readonly=True,
        store=True,
        index=True,
    )
