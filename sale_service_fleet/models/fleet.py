# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    analytic_account_ids = fields.One2many(
        comodel_name='account.analytic.account', inverse_name='vehicle_id',
        string='Contracts')
    task_ids = fields.One2many(
        comodel_name='project.task', inverse_name='vehicle_id',
        string='Tasks')
