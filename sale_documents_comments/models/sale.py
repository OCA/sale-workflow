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
        comment = res.get('sale_comment', '')
        if comment != '':
            comment = '%s ' % comment
        res['sale_comment'] = '%s%s' % (comment,
                                        order.propagated_comment or '')
        return res

    @api.multi
    def onchange_partner_id(self, partner_id):
        val = super(SaleOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            partner_obj = self.env['res.partner']
            partner = partner_obj.browse(partner_id)
            comment = partner.sale_comment or ''
            p_comment = partner.sale_propagated_comment or ''
            if partner.parent_id:
                comment = '\n%s' % (partner.parent_id.sale_comment or '')
                p_comment += (
                    '\n%s' % (partner.parent_id.sale_propagated_comment or ''))
            val['value'].update({'comment': comment,
                                 'propagated_comment': p_comment})
        return val
