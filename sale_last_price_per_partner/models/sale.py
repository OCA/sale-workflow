# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('product_id')
    def _compute_last_sale(self):
        """ Get last sale price, last sale date and last quantity """
        lines = self.env['sale.order.line'].search(
            [('product_id', '=', self.product_id.id),
             ('order_partner_id', '=', self.order_partner_id.id),
             ('state', 'in', ['sale', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        if not lines:
            return
        self.last_sale_date = lines[:1].order_id.date_order
        # check if there is more than one sale to this date
        last_date_start = self.last_sale_date + ' 00:00:00'
        last_date_end = self.last_sale_date + ' 23:59:59'
        last_date_lines = self.env['sale.order.line'].search(
            [('product_id', '=', self.product_id.id),
             ('order_partner_id', '=', self.order_partner_id.id),
             ('order_id.date_order', '>', last_date_start),
             ('order_id.date_order', '<', last_date_end),
             ('state', 'in', ['sale', 'done'])])
        # at least one line found before checked at line 21
        date_qty = sum(last_date_lines.mapped('product_uom_qty'))
        # there can be discounts so we can't use field 'price_subtotal'
        date_price = sum(
            last_date_lines.mapped('price_unit'))/len(last_date_lines)

        self.last_sale_price = date_price
        self.last_sale_qty = date_qty

    last_sale_price = fields.Float(
        string='Last Sale Price', compute='_compute_last_sale')

    last_sale_qty = fields.Integer(
        string='Last Sale Quantity', compute='_compute_last_sale')

    last_sale_date = fields.Date(
        string='Last Sale Date', compute='_compute_last_sale')
