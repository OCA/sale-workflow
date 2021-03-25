# Copyright 2017 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    account_payment_ids = fields.One2many(
        "account.payment", "sale_id", string="Pay sale advanced", readonly=True
    )
    amount_residual = fields.Float(
        "Residual amount", readonly=True, compute="_compute_get_amount_residual"
    )
    payment_line_ids = fields.Many2many(
        "account.move.line",
        string="Payment move lines",
        compute="_compute_get_payment_move_line_ids",
    )

    def _compute_get_payment_move_line_ids(self):
        for sale in self:
            sale.payment_line_ids = sale.account_payment_ids.mapped(
                "move_line_ids"
            ).filtered(lambda x: x.account_id.internal_type == "receivable")

    def _compute_get_amount_residual(self):
        for sale in self:
            advance_amount = 0.0
            for line in sale.account_payment_ids:
                if line.state != "draft":
                    advance_amount += line.amount
            sale.amount_residual = sale.amount_total - advance_amount
