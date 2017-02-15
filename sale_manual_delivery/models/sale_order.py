# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    manual_delivery = fields.Boolean(
        string='Manual Delivery',
        default=False
    )

    @api.onchange('team_id')
    def _onchange_team_id(self):
        self.manual_delivery = self.team_id.manual_delivery \
            if self.team_id else False

    @api.multi
    def action_manual_delivery_wizard(self):
        self.ensure_one()
        wizard = self.env['manual.delivery'].create({
            'order_id': self.id,
        })
        wizard.onchange_order_id()
        action = self.env.ref(
            'sale_manual_delivery.action_wizard_manual_delivery'
        ).read()[0]
        action['res_id'] = wizard.id
        return action

    @api.one
    def toggle_manual(self):
        if isinstance(self.id, int):  # if already saved
            if self.state != 'draft':
                raise UserError(_(
                    'You can only change to/from manual delivery in a quote, \
                    not a confirmed order'))
            self.manual_delivery = not self.manual_delivery
