# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_validation_blocked = fields.Boolean(
        readonly=True, tracking=True, string="Delivery Validation Blocked"
    )
    hide_button_picking_validation_blocked = fields.Boolean(
        "Display the picking validation buttons",
        help="Technical field to determine whether the "
        "picking validation buttons should be displayed",
        compute="_compute_hide_picking_validation_blocked",
        compute_sudo=True,
    )

    @api.depends("picking_validation_blocked", "state", "delivery_count")
    def _compute_hide_picking_validation_blocked(self):
        for rec in self:
            rec.hide_button_picking_validation_blocked = (
                rec.state != "sale"
                or not self.env.user.has_group("sales_team.group_sale_manager")
                or rec.delivery_count == 0
            )

    def action_block_picking_validation(self):
        self.write({"picking_validation_blocked": True})

    def action_unblock_picking_validation(self):
        self.write({"picking_validation_blocked": False})
