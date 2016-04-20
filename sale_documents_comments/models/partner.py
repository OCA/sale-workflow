# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

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
        comment_list = []
        pcomment_list = []
        if self.sale_comment:
            comment_list.append(self.sale_comment)
        if self.parent_id.sale_comment:
            comment_list.append(self.parent_id.sale_comment)
        if self.sale_propagated_comment:
            pcomment_list.append(self.sale_propagated_comment)
        if self.parent_id.sale_propagated_comment:
            pcomment_list.append(self.parent_id.sale_propagated_comment)
        return '\n'.join(comment_list), '\n'.join(pcomment_list)

    def _get_picking_comments(self):
        comment_list = []
        pcomment_list = []
        if self.picking_comment:
            comment_list.append(self.picking_comment)
        if self.parent_id.picking_comment:
            comment_list.append(self.parent_id.picking_comment)
        if self.picking_propagated_comment:
            pcomment_list.append(self.picking_propagated_comment)
        if self.parent_id.picking_propagated_comment:
            pcomment_list.append(self.parent_id.picking_propagated_comment)
        return '\n'.join(comment_list), '\n'.join(pcomment_list)

    def _get_invoice_comments(self):
        comment_list = []
        if self.invoice_comment:
            comment_list.append(self.invoice_comment)
        if self.parent_id.invoice_comment:
            comment_list.append(self.parent_id.invoice_comment)
        return '\n'.join(comment_list)
