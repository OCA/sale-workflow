# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_count = fields.Integer(
        compute='_compute_production_count')

    @api.multi
    def _compute_production_count(self):
        mrp_production_model = self.env['mrp.production']
        for sale in self:
            domain = [('sale_order_id', '=', sale.id)]
            sale.production_count = mrp_production_model.search_count(domain)

    @api.multi
    def action_view_production(self):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        productions = self.env['mrp.production'].search(
            [('sale_order_id', 'in', self.ids)])
        if len(productions) > 1:
            action['domain'] = [('id', 'in', productions.ids)]
        else:
            action['views'] = [
                (self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            action['res_id'] = productions.id
        return action
