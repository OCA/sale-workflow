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
