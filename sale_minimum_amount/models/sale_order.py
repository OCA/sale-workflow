from odoo import Command, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    minimum_so_amount = fields.Float(
        related="partner_id.minimum_so_amount",
        string="Sale Minimum Amount",
    )

    @api.constrains("partner_id", "amount_untaxed")
    def _check_minimum_amount(self):
        block_reason = self.env.ref(
            "sale_minimum_amount.minimum_amount_block_reason",
            raise_if_not_found=False,
        )
        approval_block_exception = self.env.ref(
            "sale_order_approval_block.so_excep_approval_block",
            raise_if_not_found=False,
        )
        for rec in self:
            under_min = rec.amount_untaxed < rec.minimum_so_amount
            force_release = rec.env.context.get(
                "force_so_approval_block_release", False
            )
            if under_min and not rec.approval_block_id and not force_release:
                rec.approval_block_id = block_reason
            elif not under_min and rec.approval_block_id == block_reason:
                rec.approval_block_id = False
                if (
                    approval_block_exception
                    and approval_block_exception in rec.exception_ids
                ):
                    rec.exception_ids = [Command.unlink(approval_block_exception.id)]
