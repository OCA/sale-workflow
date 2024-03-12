# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
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
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    @api.depends("partner_id")
    def _compute_delivery_block_id(self):
        """Add the 'Default Delivery Block Reason' if set in the partner."""
        for so in self:
            so.delivery_block_id = so.partner_id.default_delivery_block or False

    def action_remove_delivery_block(self):
        """Remove the delivery block and create procurements as usual."""
        order_to_unblock = self.filtered(
            lambda so: so.state == "sale" or not so.delivery_block_id
        )
        order_to_unblock.write({"delivery_block_id": False})
        order_to_unblock.order_line._action_launch_stock_rule()
        return True

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        new_so = super().copy(default=default)
        for so in new_so:
            if so.partner_id.default_delivery_block and not so.delivery_block_id:
                so.delivery_block_id = so.partner_id.default_delivery_block
        return new_so
