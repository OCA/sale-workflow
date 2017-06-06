# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_comment = fields.Text(string='Internal comments')
    sale_propagated_comment = fields.Text(
        string='Propagated internal comments')

    @api.one
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        picking_com, picking_pcom = self.partner_id._get_picking_comments()
        self.sale_comment = picking_com
        self.sale_propagated_comment = picking_pcom

    @api.returns('self', lambda value: value.id)
    @api.model
    def create(self, values):
        partner_id = values.get('partner_id', False)
        origin = values.get('origin', False)
        comment = values.get('sale_comment', '') or ''
        pcomment = values.get('sale_propagated_comment', '') or ''
        comment_list = []
        pcomment_list = []
        if partner_id:
            if origin:
                sale_obj = self.env['sale.order']
                sale = sale_obj.search([('name', '=', origin)], limit=1)
                if sale.propagated_comment:
                    pcomment_list.append(sale.propagated_comment)
            partner = self.env['res.partner'].browse(partner_id)
            picking_com, picking_pcom = partner._get_picking_comments()
            if comment:
                comment_list.append(comment)
            if picking_com:
                comment_list.append(picking_com)
            if pcomment:
                pcomment_list.append(pcomment)
            if picking_pcom:
                pcomment_list.append(picking_pcom)
            values.update({
                'sale_comment': '\n'.join(comment_list),
                'sale_propagated_comment': '\n'.join(pcomment_list)})
        return super(StockPicking, self).create(values)

    @api.model
    def _create_invoice_from_picking(self, picking, values):
        sale_comment = values.get('sale_comment', '')
        pcomment_list = []
        if sale_comment:
            pcomment_list.append(sale_comment)
        if picking.sale_propagated_comment:
            pcomment_list.append(picking.sale_propagated_comment
                                 )
        partner_id = values.get('partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner._get_invoice_comments():
                pcomment_list.append(partner._get_invoice_comments())
        values['sale_comment'] = '\n'.join(pcomment_list)
        return super(StockPicking, self)._create_invoice_from_picking(
            picking, values)
