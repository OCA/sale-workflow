# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ManualLine(models.TransientModel):
    _name = "manual.line"

    manual_delivery_id = fields.Many2one(
        'manual.delivery',
        string='Wizard manual procurement',
    )
    order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
    )
    ordered_qty = fields.Float(
        'Ordered Quantity',
        readonly=True,
    )
    remaining = fields.Float(
        'Remaining',
        compute='compute_remaining',
        readonly=True,
    )
    product_qty = fields.Float(
        'Quantity to Ship',
    )

    @api.multi
    @api.depends('product_qty')
    def compute_remaining(self):
        for line in self:
            line.remaining = line.ordered_qty - line.product_qty
