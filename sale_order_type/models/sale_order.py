# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_order_type(self):
        return self.env['sale.order.type'].search([], limit=1)

    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', default=_get_order_type)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.type_id = \
                self.partner_id.sale_type.id or self._get_order_type().id
        return super(SaleOrder, self).onchange_partner_id()

    @api.one
    @api.onchange('type_id')
    def onchange_type_id(self):
        self.warehouse_id = self.type_id.warehouse_id
        self.picking_policy = self.type_id.picking_policy
        if self.type_id.payment_term_id:
            self.payment_term_id = self.type_id.payment_term_id.id
        if self.type_id.pricelist_id:
            self.pricelist_id = self.type_id.pricelist_id.id
        if self.type_id.incoterm_id:
            self.incoterm = self.type_id.incoterm_id.id

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/'and vals.get('type_id'):
            type = self.env['sale.order.type'].browse(vals['type_id'])
            if type.sequence_id:
                vals['name'] = type.sequence_id.next_by_id()
        return super(SaleOrder, self).create(vals)

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.type_id.journal_id:
            res['journal_id'] = self.type_id.journal_id.id
        if self.type_id:
            res['sale_type_id'] = self.type_id.id
        return res
