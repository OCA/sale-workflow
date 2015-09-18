# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_order_type(self):
        return self.env['sale.order.type'].search([])[:1]

    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', default=_get_order_type)

    @api.multi
    def onchange_partner_id(self, part):
        res = super(SaleOrder, self).onchange_partner_id(part)
        if part:
            partner = self.env['res.partner'].browse(part)
            res['value'].update({
                'type_id': partner.sale_type.id or self._get_order_type().id,
            })
        return res

    @api.one
    @api.onchange('type_id')
    def onchange_type_id(self):
        self.warehouse_id = self.type_id.warehouse_id
        self.picking_policy = self.type_id.picking_policy
        self.order_policy = self.type_id.order_policy

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/'and vals.get('type_id'):
            type = self.env['sale.order.type'].browse(vals['type_id'])
            if type.sequence_id:
                sequence_obj = self.env['ir.sequence']
                vals['name'] = sequence_obj.next_by_id(type.sequence_id.id)
        return super(SaleOrder, self).create(vals)

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        vals = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id=group_id)
        vals['invoice_state'] = order.type_id.invoice_state
        return vals

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(SaleOrder, self)._prepare_invoice(order, line_ids)
        if order.type_id.journal_id:
            res['journal_id'] = order.type_id.journal_id.id
        return res
