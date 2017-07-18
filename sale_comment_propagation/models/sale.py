# -*- coding: utf-8 -*-
# Copyright 2015 Ainara Galdona - AvanzOSC
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    comment = fields.Text(string='Internal comments')
    propagated_comment = fields.Text(string='Propagated internal comments')

    @api.multi
    def _prepare_invoice(self):
        comment_list = []
        res = super(SaleOrder, self)._prepare_invoice()
        sale_comment = res.get('sale_comment')
        partner_id = res.get('partner_id', self.partner_invoice_id.id)
        if sale_comment:
            comment_list.append(sale_comment)
        if self.propagated_comment:
            comment_list.append(self.propagated_comment)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner._get_invoice_comments():
                comment_list.append(partner._get_invoice_comments())
        res['sale_comment'] = '\n'.join(comment_list)
        return res

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        comment, pcomment = self.partner_id._get_sale_comments()
        self.comment = comment
        self.propagated_comment = pcomment
        return res
