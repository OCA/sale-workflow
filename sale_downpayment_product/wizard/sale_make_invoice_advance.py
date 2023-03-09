# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    product_id = fields.Many2one(
        domain=[
            ("type", "=", "service"),
            ("is_down_payment_product", "=", True),
        ]
    )
