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
    def on_change_type_id(self, type_id):
        if type_id:
            type = self.env['sale.order.type'].browse(type_id)
            return {'value': {'warehouse_id': type.warehouse_id.id}}
        return {}

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/'and vals.get('type_id'):
            type = self.env['sale.order.type'].browse(vals['type_id'])
            if type.sequence_id:
                sequence_obj = self.env['ir.sequence']
                vals['name'] = sequence_obj.next_by_id(type.sequence_id.id)
        return super(SaleOrder, self).create(vals)

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(SaleOrder, self)._prepare_invoice(order, line_ids)
        res['journal_id'] = order.type_id.journal_id.id
        return res
