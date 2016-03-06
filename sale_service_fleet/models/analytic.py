# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class FleetAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle', string='Vehicle')
