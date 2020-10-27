# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    picking_validation_blocked = fields.Boolean(
        readonly=True, track_visibility="onchange", string="Delivery Validation Blocked"
    )

    def action_block_picking_validation(self):
        self.write({"picking_validation_blocked": True})

    def action_unblock_picking_validation(self):
        self.write({"picking_validation_blocked": False})
