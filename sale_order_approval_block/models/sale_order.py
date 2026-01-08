# Copyright 2026 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_block_id = fields.Many2one(
        comodel_name="sale.approval.block.reason",
        string="Approval Block Reason",
    )
    approval_blocked = fields.Boolean(
        compute="_compute_approval_blocked",
    )

    @api.depends("approval_block_id")
    def _compute_approval_blocked(self):
        for rec in self:
            rec.approval_blocked = bool(rec.approval_block_id)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for vals, so in zip(vals_list, records, strict=False):
            if vals.get("approval_block_id"):
                so.message_post(
                    body=self.env._(
                        'Order "%(order)s" blocked with reason "%(reason)s"',
                        order=so.name,
                        reason=so.approval_block_id.name,
                    )
                )
        return records

    def write(self, vals):
        res = super().write(vals)
        for so in self:
            if vals.get("approval_block_id"):
                so.message_post(
                    body=self.env._(
                        'Order "%(order)s" blocked with reason "%(reason)s"',
                        order=so.name,
                        reason=so.approval_block_id.name,
                    )
                )
            elif "approval_block_id" in vals and not vals["approval_block_id"]:
                so.message_post(
                    body=self.env._(
                        'Order "%(order)s" approval block released.',
                        order=so.name,
                    )
                )
        return res

    def button_release_approval_block(self):
        for order in self:
            order.approval_block_id = False
        return True
