# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_comment = fields.Text(string='Comments for sale orders')
    sale_propagated_comment = fields.Text(
        string='Propagated comments for sale orders')
    picking_comment = fields.Text(string='Comments for pickings')
    picking_propagated_comment = fields.Text(
        string='Propagated comments for pickings')
    invoice_comment = fields.Text(string='Comments for invoices')

    def _get_sale_comments(self):
        comment = self.sale_comment or ''
        pcomment = self.sale_propagated_comment or ''
        if self.parent_id:
            comment += '\n%s' % (self.parent_id.sale_comment or '')
            pcomment += '\n%s' % (self.parent_id.sale_propagated_comment or
                                  '')
        return comment, pcomment

    def _get_picking_comments(self):
        comment = self.picking_comment or ''
        pcomment = self.picking_propagated_comment or ''
        if self.parent_id:
            comment += '\n%s' % (self.parent_id.picking_comment or '')
            pcomment += '\n%s' % (self.parent_id.picking_propagated_comment or
                                  '')
        return comment, pcomment

    def _get_invoice_comments(self):
        comment = self.invoice_comment or ''
        if self.parent_id:
            comment += '\n%s' % (self.parent_id.invoice_comment or '')
        return comment
