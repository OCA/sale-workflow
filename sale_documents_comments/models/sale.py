# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    comment = fields.Text(string='Internal comments')
    propagated_comment = fields.Text(string='Propagated internal comments')

    @api.model
    def _prepare_invoice(self, order, lines):
        res = super(SaleOrder, self)._prepare_invoice(order, lines)
        sale_comment = res.get('sale_comment', '')
        partner_id = res.get('partner_id', order.partner_invoice_id.id)
        sale_comment += '\n%s' % (order.propagated_comment or '')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            sale_comment += '\n%s' % (partner._get_invoice_comments() or '')
        res['sale_comment'] = sale_comment
        return res

    @api.multi
    def onchange_partner_id(self, partner_id):
        val = super(SaleOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            comment, pcomment = partner._get_sale_comments()
            val['value'].update({'comment': comment,
                                 'propagated_comment': pcomment})
        return val
