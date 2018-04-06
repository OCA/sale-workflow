# -*- coding: utf-8 -*-
# © 2015 Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProcurementGroup(models.Model):

    _inherit = 'procurement.group'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

