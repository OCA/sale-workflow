# Copyright 2026 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleApprovalBlockReason(models.Model):
    _name = "sale.approval.block.reason"
    _description = "Sale Approval Block Reason"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
