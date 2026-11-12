# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    invoice_plan_group = fields.Integer(
        default=1,
        copy=True,
        help="Group this line with others for the 'Sequential Grouped' "
        "invoice plan method. Lines sharing the same group number are invoiced "
        "together over max(qty) installments of 1 unit each; when the group is "
        "fully invoiced, the next group begins.",
    )
