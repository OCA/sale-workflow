# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    min_dt = fields.Date(
        string='Scheduled Date (for filter purpose only)',
        compute='_compute_min_dt', store=True)

    @api.multi
    @api.depends('scheduled_date')
    def _compute_min_dt(self):
        for picking in self:
            min_dt = fields.Date.from_string(picking.scheduled_date)
            picking.min_dt = min_dt
