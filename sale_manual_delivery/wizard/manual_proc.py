# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import UserError
from odoo.tools.translate import _

class ManualDelivery(models.TransientModel):
    """Creates procurements manually"""
    _name = "manual.delivery"
    _order = 'create_date desc'

    def _set_order_id(self):
        return self.env['sale.order'].browse(self._context['active_ids'])

    @api.onchange('order_id')
    def onchange_order_id(self):
        lines = []
        if self.order_id:
            for line in self.order_id.order_line:
                if not line.existing_qty == line.product_uom_qty and \
                line.product_id.type != 'service':
                    vals = {
                        'order_line_id': line.id,
                        'ordered_qty': line.product_uom_qty,
                        'existing_qty': line.existing_qty
                    }
                    lines.append((0, 0, vals))
            self.update({'line_ids': lines})

    date_planned = fields.Date(
        string='Date Planned',
        required=True
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',  # TODO HIDE
        default=_set_order_id
    )
    line_ids = fields.One2many(
        'manual.delivery.line',
        'manual_delivery_id',
        string='Lines to validate',
    )
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string='Delivery Method'
    )

    @api.multi
    def record_picking(self):
        for wizard in self:
            carrier_id = wizard.carrier_id if wizard.carrier_id else \
              wizard.order_id.carrier_id
            date_planned = wizard.date_planned
            for line in wizard.line_ids:
                if line.to_ship_qty > line.ordered_qty - line.existing_qty:
                    raise UserError(_(
                    'You can not deliver more than the remaining quantity. If\
                    you need to do so, please edit the sale order first.'))
                if float_compare(line.to_ship_qty, 0, 2):
                    to_ship_qty = line.to_ship_qty
                    line.order_line_id._action_manual_procurement_create(
                        to_ship_qty, date_planned, carrier_id)
