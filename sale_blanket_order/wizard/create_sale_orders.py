# coding: utf-8
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class BlanketOrderWizard(models.TransientModel):
    _name = 'sale.blanket.order.wizard'
    _description = 'Blanket Order Wizard'

    @api.model
    def _default_order(self):
        # in case the cron hasn't run
        self.env['sale.blanket.order'].expire_orders()
        if not self.env.context.get('active_id'):
            return False
        blanket_order = self.env['sale.blanket.order'].browse(
            self.env.context['active_id'])
        if blanket_order.state == 'expired':
            raise UserError(_('You can\'t create a sale order from '
                              'an expired blanket order!'))
        return blanket_order

    @api.model
    def _default_lines(self):
        blanket_order = self._default_order()
        lines = [(0, 0, {
            'blanket_line_id': l.id,
            'product_id': l.product_id.id,
            'remaining_qty': l.remaining_qty,
            'qty': l.remaining_qty,
        }) for l in blanket_order.lines_ids]
        return lines

    blanket_order_id = fields.Many2one(
        'sale.blanket.order', default=_default_order, readonly=True)
    lines_ids = fields.One2many(
        'sale.blanket.order.wizard.line', 'wizard_id',
        string='Lines', default=_default_lines)

    @api.multi
    def create_sale_order(self):
        self.ensure_one()

        line_obj = self.env['sale.order.line']
        order_lines = []
        for line in self.lines_ids:
            if line.qty == 0.0:
                continue

            if line.qty > line.remaining_qty:
                raise UserError(
                    _('You can\'t order more than the remaining quantities'))

            vals = {
                'product_id': line.product_id.id,
                'product_uom': line.blanket_line_id.product_uom.id,
                'sequence': line.blanket_line_id.sequence,
                'price_unit': line.blanket_line_id.price_unit,
                'blanket_line_id': line.blanket_line_id.id,
            }
            vals.update(line_obj.onchange(
                vals, 'product_id', {'product_id': 'true'})['value'])
            vals['product_uom_qty'] = line.qty
            order_lines.append((0, 0, vals))

        if not order_lines:
            raise UserError(_('An order can\'t be empty'))

        order_vals = {
            'partner_id': self.blanket_order_id.partner_id.id,
        }
        order_vals.update(self.env['sale.order'].onchange(
            order_vals, 'partner_id', {'partner_id': 'true'})['value'])
        order_vals.update({
            'user_id': self.blanket_order_id.user_id.id,
            'origin': self.blanket_order_id.name,
            'currency_id': self.blanket_order_id.currency_id.id,
            'order_line': order_lines,
            'pricelist_id': (self.blanket_order_id.pricelist_id.id
                             if self.blanket_order_id.pricelist_id
                             else False),
            'payment_term_id': (self.blanket_order_id.payment_term_id.id
                                if self.blanket_order_id.payment_term_id
                                else False),
        })

        sale_order = self.env['sale.order'].create(order_vals)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
        }


class BlanketOrderWizardLine(models.TransientModel):
    _name = 'sale.blanket.order.wizard.line'

    wizard_id = fields.Many2one('sale.blanket.order.wizard')
    blanket_line_id = fields.Many2one(
        'sale.blanket.order.line')
    product_id = fields.Many2one(
        'product.product',
        related='blanket_line_id.product_id',
        string='Product', readonly=True)
    remaining_qty = fields.Float(
        related='blanket_line_id.remaining_qty', readonly=True)
    qty = fields.Float(string='Quantity to Order', required=True)
