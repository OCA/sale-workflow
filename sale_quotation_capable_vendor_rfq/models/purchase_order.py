# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_quotation_id = fields.Many2one(
        "sale.order",
        string="Quotation",
        help="Quotation this purchase order was created from",
    )
