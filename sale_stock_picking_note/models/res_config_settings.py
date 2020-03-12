# Copyright 2020 Daniel Reis - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_sale_picking_note_edit = fields.Boolean(
        string="Edit picking notes after confirming the Sales Order",
        implied_group="sale_stock_picking_note.group_sale_picking_note_edit")
