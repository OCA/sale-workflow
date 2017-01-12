# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools import float_compare


class ManualProcurement(models.TransientModel):
    """Creates procurements manually"""
    _name = "manual.procurement"
    _order = 'create_date desc'

    def _set_order_id(self):
        return self.env['sale.order'].browse(self._context['active_ids'])

    @api.onchange('order_id')
    def onchange_order_id(self):
        lines = []
        if self.order_id:
            for line in self.order_id.order_line:

                vals = {
                    'order_line_id': line.id,
                    'ordered_qty': line.product_uom_qty
                }
                lines.append((0, 0, vals))
            self.update({'line_ids': lines})

    date_planned = fields.Date(
        string='Date Planned'
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',  # TODO HIDE
        default=_set_order_id
    )
    line_ids = fields.One2many(
        'manual.line',
        'manual_proc_id',
        string='Lines to validate',
    )
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string='Delivery Method',
    )

    @api.multi
    def record_picking(self):
        for wizard in self:
            carrier_id = wizard.carrier_id
            date_planned = wizard.date_planned
            for line in wizard.line_ids:
                if float_compare(line.product_qty, 0, 2):
                    product_qty = line.product_qty
                    so_line = line.order_line_id._action_manual_procurement_create(
                        product_qty, date_planned, carrier_id)
