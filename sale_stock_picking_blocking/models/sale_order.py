# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# Copyright 2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_block_id = fields.Many2one(
        comodel_name="sale.delivery.block.reason",
        tracking=True,
        string="Delivery Block Reason",
        compute="_compute_delivery_block_id",
        store=True,
        precompute=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    def action_done(self):
        return super(
            SaleOrder, self.filtered(lambda s: not s.delivery_block_id)
        ).action_done()

    @api.depends("partner_id", "payment_term_id")
    def _compute_delivery_block_id(self):
        """Set a default delivery block reason from partner or payment term,
        but do not overwrite an already existing value."""
        for so in self:
            if so.delivery_block_id:
                continue
            so.delivery_block_id = (
                so.partner_id.default_delivery_block
                or so.payment_term_id.default_delivery_block_reason_id
                or False
            )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order, vals in zip(orders, vals_list):
            if not vals.get("delivery_block_id"):
                continue
            order.delivery_block_id = vals["delivery_block_id"]
        return orders

    def write(self, vals):
        preserved = {}
        if "delivery_block_id" not in vals and (
            "partner_id" in vals or "payment_term_id" in vals
        ):
            preserved = {
                so.id: so.delivery_block_id.id for so in self if so.delivery_block_id
            }
        res = super().write(vals)
        if not preserved:
            return res
        for so in self:
            preserved_id = preserved.get(so.id)
            if not preserved_id:
                continue
            if so.delivery_block_id:
                continue
            so.delivery_block_id = preserved_id
        return res

    def action_remove_delivery_block(self):
        """Remove the delivery block and create procurements as usual."""
        order_to_unblock = self.filtered(
            lambda so: so.state == "sale" or not so.delivery_block_id
        )
        order_to_unblock.write({"delivery_block_id": False})
        order_to_unblock.order_line._action_launch_stock_rule()
        if self.user_has_groups("sale.group_auto_done_setting"):
            order_to_unblock.action_done()
        return True

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        new_so = super().copy(default=default)
        for so in new_so:
            if so.partner_id.default_delivery_block and not so.delivery_block_id:
                so.delivery_block_id = so.partner_id.default_delivery_block
            elif (
                so.payment_term_id.default_delivery_block_reason_id
                and not so.delivery_block_id
            ):
                so.delivery_block_id = (
                    so.payment_term_id.default_delivery_block_reason_id
                )
        return new_so
