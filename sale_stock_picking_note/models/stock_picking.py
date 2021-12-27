# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    note = fields.Text(track_visibility="onchange")
