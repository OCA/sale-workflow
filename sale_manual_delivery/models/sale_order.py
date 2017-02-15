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
        self.manual_procurement = self.team_id.manual_procurement \
            if self.team_id else False

    @api.multi
    def action_manual_procurement_wizard(self):
        self.ensure_one()
        wizard = self.env['manual.procurement'].create({
            'order_id': self.id,
        })
        wizard.onchange_order_id()
        action = self.env.ref(
            'sale_manual_delivery.action_wizard_manual_procurement'
        ).read()[0]
        action['res_id'] = wizard.id
        return action
