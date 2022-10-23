# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_elaboration_note_on_delivery_slip = fields.Boolean(
        "Display Elaboration notes on Delivery Slips",
        implied_group="sale_elaboration.group_elaboration_note_on_delivery_slip",
    )
