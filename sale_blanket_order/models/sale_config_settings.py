# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    group_blanket_disable_adding_lines = fields.Boolean(
        string="Disable adding more lines to SOs",
        implied_group="sale_blanket_order.blanket_orders_disable_adding_lines",
    )
    blanket_order_seq_number_from_draft = fields.Boolean(
        related="company_id.blanket_order_seq_number_from_draft",
        readonly=False,
    )
