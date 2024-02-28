# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    so_line_order_default = fields.Many2one(
        related="company_id.default_so_line_order",
        string="Line Order 1",
        readonly=False,
    )
    so_line_order_2_default = fields.Many2one(
        related="company_id.default_so_line_order_2",
        string="Line Order 2",
        readonly=False,
    )
    so_line_direction_default = fields.Selection(
        related="company_id.default_so_line_direction",
        string="Sort Direction",
        readonly=False,
    )

    @api.onchange("so_line_order_default")
    def onchange_so_line_order_default(self):
        """Reset direction line order when user remove order field value"""
        if not self.so_line_order_default and not self.so_line_order_2_default:
            self.so_line_direction_default = False
