# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_comment = fields.Text(string='Internal comments')
    sale_propagated_comment = fields.Text(
        string='Propagated internal comments')

    @api.one
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        picking_com = ''
        picking_pcom = ''
        if self.partner_id:
            picking_com = self.partner_id.picking_comment or ''
            picking_pcom = self.partner_id.picking_propagated_comment or ''
            parent = self.partner_id.parent_id
            if parent:
                picking_com += '\n%s' % (parent.picking_comment or '')
                picking_pcom += '\n%s' % (parent.picking_propagated_comment or
                                          '')
        self.sale_comment = picking_com
        self.sale_propagated_comment = picking_pcom

    @api.model
    def create(self, values):
        partner_id = values.get('partner_id', False)
        origin = values.get('origin', False)
        comment = values.get('sale_comment', '')
        pcomment = values.get('sale_propagated_comment', '')
        if partner_id:
            partner_obj = self.env['res.partner']
            if origin:
                sale_obj = self.env['sale.order']
                sale = sale_obj.search([('name', '=', origin)], limit=1)
                pcomment += '\n%s' % (sale.propagated_comment or '')
            partner = partner_obj.browse(partner_id)
            picking_com = partner.picking_comment or ''
            picking_pcom = partner.picking_propagated_comment or ''
            if partner.parent_id:
                picking_com += '\n%s' % (partner.parent_id.picking_comment or
                                         '')
                picking_pcom += ('\n%s' %
                                 (partner.parent_id.picking_propagated_comment
                                  or ''))
            if comment != picking_com:
                comment += '\n%s' % (picking_com or '')
            if pcomment != picking_pcom:
                pcomment += '\n%s' % (picking_pcom or '')
            values.update({'sale_comment': comment,
                           'sale_propagated_comment': pcomment})
        return super(StockPicking, self).create(values)

    @api.model
    def _create_invoice_from_picking(self, picking, values):
        if 'sale_comment' not in values:
            values['sale_comment'] = ''
        values['sale_comment'] = ('%s\n%s' %
                                  (values['sale_comment'],
                                   picking.sale_propagated_comment or ''))
        return super(StockPicking, self)._create_invoice_from_picking(picking,
                                                                      values)
