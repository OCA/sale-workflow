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
        picking_com, picking_pcom = self.partner_id._get_picking_comments()
        self.sale_comment = picking_com
        self.sale_propagated_comment = picking_pcom

    @api.model
    def create(self, values):
        partner_id = values.get('partner_id', False)
        origin = values.get('origin', False)
        comment = values.get('sale_comment', '') or ''
        pcomment = values.get('sale_propagated_comment', '') or ''
        if partner_id:
            if origin:
                sale_obj = self.env['sale.order']
                sale = sale_obj.search([('name', '=', origin)], limit=1)
                pcomment += '\n%s' % (sale.propagated_comment or '')
            partner = self.env['res.partner'].browse(partner_id)
            picking_com, picking_pcom = partner._get_picking_comments()
            comment += '\n%s' % (picking_com or '')
            pcomment += '\n%s' % (picking_pcom or '')
            values.update({'sale_comment': comment,
                           'sale_propagated_comment': pcomment})
        return super(StockPicking, self).create(values)

    @api.model
    def _create_invoice_from_picking(self, picking, values):
        sale_comment = values.get('sale_comment', '')
        sale_comment += (
            '\n%s' % (picking.sale_propagated_comment or ''))
        partner_id = values.get('partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            sale_comment += '\n%s' % (partner._get_invoice_comments() or '')
        values['sale_comment'] = sale_comment
        return super(StockPicking, self)._create_invoice_from_picking(
            picking, values)
