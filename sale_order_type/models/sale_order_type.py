# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import fields, models


class SaleOrderTypology(models.Model):
    _name = 'sale.order.type'
    _description = 'Type of sale order'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Entry Sequence', copy=False)
    journal_id = fields.Many2one(
        comodel_name='account.journal', string='Billing Journal')
    refund_journal_id = fields.Many2one(
        comodel_name='account.journal', string='Refund Billing Journal')
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse', required=True)
