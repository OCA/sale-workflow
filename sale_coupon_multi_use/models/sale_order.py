from odoo import fields, models

ORDER_CTX_KEY = "coupon_sale_order"


class SaleOrder(models.Model):
    """Extend to modify action_confirm for multi-use coupons."""

    _inherit = "sale.order"

    coupon_multi_use_ids = fields.Many2many(
        "sale.coupon",
        "sale_order_coupon_multi_rel",
        "sale_id",
        "coupon_id",
        string="Multi Use Coupons",
        copy=False,
        readonly=True,
    )

    def _get_multi_use_coupons(self):
        self.ensure_one()
        # NOTE. This method must be called with ORDER_CTX_KEY on order.
        return self.coupon_multi_use_ids - self.applied_coupon_ids

    def action_confirm(self):
        """Extend to pass coupon_sale_order context."""
        for order in self:
            # Mimic same behavior as for single-user coupon.
            order = order.with_context(**{ORDER_CTX_KEY: order})
            super(SaleOrder, order).action_confirm()
            order._get_multi_use_coupons().consume_coupons()
        return True

    def action_cancel(self):
        """Extend to pass coupon_sale_order context."""
        for order in self:
            order = order = order.with_context(**{ORDER_CTX_KEY: order})
            super(SaleOrder, order).action_cancel()
            order._get_multi_use_coupons().reset_coupons()
            # Mimic applied_coupon_ids logic.
            order.coupon_multi_use_ids = [(5,)]
        return True

    def write(self, vals):
        """Extend to add multi-use coupons."""
        res = super().write(vals)
        applied_coupon_ids = vals.get("applied_coupon_ids", [])
        # Only care to move if coupons were added (4 or 6 cmd).
        if any(cmd[0] in (4, 6) for cmd in applied_coupon_ids):
            # Not very optimal to write multiple times, but moving ids
            # between 2many commands (before write) is more complicated.
            for order in self:
                ids_to_move = order.applied_coupon_ids.filtered("multi_use").ids
                if ids_to_move:
                    order.write(
                        {
                            # Detach from single use coupons.
                            "applied_coupon_ids": [(3, _id) for _id in ids_to_move],
                            # Must use cmd 4 instead of 6, to not overwrite existing
                            # coupons.
                            "coupon_multi_use_ids": [(4, _id) for _id in ids_to_move],
                        }
                    )
        return res


class SaleOrderLine(models.Model):
    """Extend to reverse relate with consumption line."""

    _inherit = "sale.order.line"

    def unlink(self):
        """Extend to reactivate/reset removed multi-use coupons."""
        related_program_lines = self.env["sale.order.line"]
        # Reactivate coupons related to unlinked reward line
        for line in self.filtered(lambda line: line.is_reward_line):
            order = line.order_id
            coupons_to_detach = order.coupon_multi_use_ids.filtered(
                lambda r: r.program_id.discount_line_product_id == line.product_id
            )
            # We can only reactivate coupons that are not part of
            # applied_coupon_ids, because that part will signal
            # reactivate too.
            coupons_to_reactivate = (
                coupons_to_detach
                - order.applied_coupon_ids.filtered(
                    lambda r: r.program_id.discount_line_product_id == line.product_id
                )
            )
            coupons_to_reactivate.reset_coupons()
            order.coupon_multi_use_ids -= coupons_to_detach
            # Remove the program from the order if the deleted line is
            # the reward line of the program.
            # And delete the other lines from this program (It's the
            # case when discount is split per different taxes)
            related_program = self.env["sale.coupon.program"].search(
                [("discount_line_product_id", "=", line.product_id.id)]
            )
            if related_program:
                # No need to remove promotions, because multi-use
                # coupons are not related with promotions.
                related_program_lines |= (
                    order.order_line.filtered(
                        lambda l: l.product_id
                        == related_program.discount_line_product_id
                    )
                    - line
                )
        return super(SaleOrderLine, self | related_program_lines).unlink()
