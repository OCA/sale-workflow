# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    manual_procurement = fields.Boolean(
        string='Manual Procurement',
        default=False
    )

    @api.onchange('team_id')
    def _onchange_team_id(self):
        self.manual_procurement = False  # "TODO copy sale team value"
