# coding: utf-8
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BlanketPlannedOrder(models.Model):
    _name = 'sale.blanket.planned.order'
    _description = 'Blanket Planned Order'
    blanket_order_id = fields.Many2one(
        'sale.blanket.order', required=True, ondelete='cascade')
    next_order_date = fields.Date(required=True)
    line_ids = fields.One2many(
        'sale.blanket.planned.order.line', 'planned_order_id',
        string='Order Lines', copy=False)

    @api.model
    def _scheduler_create_order(self):
        domain = [('next_order_date', '=', fields.Date.today())]
        planned_orders = self.search(domain)
        planned_orders.create_order()

    @api.multi
    def create_order(self):
        line_obj = self.env['sale.order.line']
        sale_order_obj = self.env['sale.order']
        for rec in self.filtered(
                lambda r: r.next_order_date == fields.Date.today()):
            order_lines = []
            for line in rec.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.blanket_order_line_id.product_uom.id,
                    'sequence': line.blanket_order_line_id.sequence,
                    'price_unit': line.blanket_order_line_id.price_unit,
                    'blanket_line_id': line.blanket_order_line_id.id,
                }
                vals.update(line_obj.onchange(
                    vals, 'product_id', {'product_id': 'true'})['value'])
                vals['product_uom_qty'] = line.next_order_qty
                order_lines.append((0, 0, vals))

            if not order_lines:
                raise UserError(_('An order can\'t be empty'))

            order_vals = {
                'partner_id': rec.blanket_order_id.partner_id.id,
            }
            order_vals.update(rec.env['sale.order'].onchange(
                order_vals, 'partner_id', {'partner_id': 'true'})['value'])
            order_vals.update({
                'blanket_order_id': rec.blanket_order_id.id,
                'user_id': rec.blanket_order_id.user_id.id,
                'origin': rec.blanket_order_id.name,
                'currency_id': rec.blanket_order_id.currency_id.id,
                'order_line': order_lines,
                'pricelist_id': (rec.blanket_order_id.pricelist_id.id
                                 if rec.blanket_order_id.pricelist_id
                                 else False),
                'payment_term_id': (rec.blanket_order_id.payment_term_id.id
                                    if rec.blanket_order_id.payment_term_id
                                    else False),
            })
            sale_order_obj.create(order_vals)
            rec.unlink()


class BlanketPlannedOrderLine(models.Model):
    _name = 'sale.blanket.planned.order.line'
    _description = 'Blanket Planned Order Line'

    planned_order_id = fields.Many2one(
        'sale.blanket.planned.order', ondelete='cascade')
    next_order_qty = fields.Float(required=True)
    blanket_order_line_id = fields.Many2one(
        'sale.blanket.order.line', readonly=True)
    remaining_qty = fields.Float(string='Remaining Quantity',
                                 related='blanket_order_line_id.remaining_qty')
    product_id = fields.Many2one(string='Product',
                                 related='blanket_order_line_id.product_id')
    next_order_date = fields.Date(related='planned_order_id.next_order_date')
