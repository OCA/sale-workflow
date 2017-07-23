# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    comment = fields.Text(string='Internal comments')
    propagated_comment = fields.Text(string='Propagated internal comments')

    @api.model
    def _prepare_invoice(self, order, lines):
        comment_list = []
        res = super(SaleOrder, self)._prepare_invoice(order, lines)
        sale_comment = res.get('sale_comment')
        partner_id = res.get('partner_id', order.partner_invoice_id.id)
        if sale_comment:
            comment_list.append(sale_comment)
        if order.propagated_comment:
            comment_list.append(order.propagated_comment)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner._get_invoice_comments():
                comment_list.append(partner._get_invoice_comments())
        res['sale_comment'] = '\n'.join(comment_list)
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
