# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    group_blanket_disable_adding_lines = fields.Boolean(
        string="Disable adding more lines to SOs",
        implied_group="sale_blanket_order.blanket_orders_disable_adding_lines",
    )
    enable_numbered_bo = fields.Boolean(
        related="company_id.enable_numbered_bo",
        readonly=False,
    )
