# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_cancel_confirm = fields.Boolean(
        string="Sale Cancellation Reason",
        help="Ask for an optional reason when cancelling a sales order.",
    )
