# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleBlanketOrderLine(models.Model):
    _inherit = "sale.blanket.order.line"

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        related="order_id.analytic_account_id",
        string="Analytic Account",
    )

    contracted_qty = fields.Float(
        readonly=True,
    )
