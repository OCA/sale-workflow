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
        default=False,
        help="If Manual, the deliveries are not created at SO confirmation. "
             "You need to use the Create Delivery button in order to reserve "
             "and ship the goods."
    )

    @api.onchange('team_id')
    def _onchange_team_id(self):
        for so in self:
            if so.team_id:
                so.manual_delivery = so.team_id.manual_delivery
            else:
                so.manual_delivery = False

    @api.multi
    def action_manual_delivery_wizard(self):
        self.ensure_one()
        wizard = self.env['manual.delivery'].create({})
        action = self.env.ref(
            'sale_manual_delivery.action_wizard_manual_delivery'
        ).read()[0]
        action['res_id'] = wizard.id
        return action

    @api.multi
    def toggle_manual(self):
        for so in self:
            if not isinstance(so.id, models.NewId):  # if already saved
                if so.state != 'draft':
                    raise UserError(_(
                        'You can only change to/from manual delivery in a '
                        'quote, not a confirmed order'))
            so.manual_delivery = not so.manual_delivery

    @api.multi
    @api.depends('procurement_group_id')
    def _compute_picking_ids(self):
        super(SaleOrder, self)._compute_picking_ids()
        for order in self:
            proc_group = self.env['procurement.group'].search(
                [
                    ('procurement_ids.sale_line_id.order_id', '=',
                     order.id),
                ]
            )
            order.picking_ids = self.env['stock.picking'].search(
                [('group_id', 'in', proc_group.ids)]) if proc_group else []
            order.delivery_count = len(order.picking_ids)
