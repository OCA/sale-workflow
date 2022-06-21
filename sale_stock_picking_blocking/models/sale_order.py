# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("delivery_block_id")
    def _check_not_auto_done(self):
        auto_done = self.env["ir.default"].get(
            "res.config.settings", "group_auto_done_setting"
        )
        if auto_done and any(so.delivery_block_id for so in self):
            raise ValidationError(
                _('You cannot block a sale order with "auto_done_setting" ' "active.")
            )

    delivery_block_id = fields.Many2one(
        comodel_name="sale.delivery.block.reason",
        track_visibility="always",
        string="Delivery Block Reason",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """Add the 'Default Delivery Block Reason' if set in the partner."""
        res = super(SaleOrder, self).onchange_partner_id()
        for so in self:
            so.delivery_block_id = so.partner_id.default_delivery_block or False
        return res

    def action_remove_delivery_block(self):
        """Remove the delivery block and create procurements as usual."""
        for order in self.filtered(
            lambda so: so.state == "sale" or not so.delivery_block_id
        ):
            order.write({"delivery_block_id": False})
            order.order_line._action_launch_stock_rule()
        return True

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        new_so = super(SaleOrder, self).copy(default=default)
        for so in new_so:
            if so.partner_id.default_delivery_block and not so.delivery_block_id:
                so.delivery_block_id = so.partner_id.default_delivery_block
        return new_so


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        return super(
            SaleOrderLine,
            self.filtered(lambda line: not line.order_id.delivery_block_id),
        )._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
