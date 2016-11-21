# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_order_type(self):
        return self.env['sale.order.type'].search([])[:1]

    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', default=_get_order_type)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            self.type_id = self.partner_id.sale_type or self._get_order_type()

    @api.multi
    @api.onchange('type_id')
    def onchange_type_id(self):
        for order in self:
            order.warehouse_id = order.type_id.warehouse_id
            order.picking_policy = order.type_id.picking_policy

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/'and vals.get('type_id'):
            type = self.env['sale.order.type'].browse(vals['type_id'])
            if type.sequence_id:
                vals['name'] = type.sequence_id.next_by_id()
        return super(SaleOrder, self).create(vals)

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        vals = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id=group_id)
        return vals

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(SaleOrder, self)._prepare_invoice(order, line_ids)
        if order.type_id.journal_id:
            res['journal_id'] = order.type_id.journal_id.id
        return res
