# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models


class SaleOrderTypology(models.Model):
    _name = 'sale.order.type'
    _description = 'Type of sale order'

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref('sale.seq_type_sale_order')
        domain = [('code', '=', seq_type.code)]
        return domain

    @api.model
    def _get_selection_picking_policy(self):
        return self.env['sale.order'].fields_get(
            allfields=['picking_policy'])['picking_policy']['selection']

    def default_picking_policy(self):
        default_dict = self.env['sale.order'].default_get(['picking_policy'])
        return default_dict.get('picking_policy')

    @api.model
    def _get_selection_order_policy(self):
        return self.env['sale.order'].fields_get(
            allfields=['order_policy'])['order_policy']['selection']

    def default_order_policy(self):
        default_dict = self.env['sale.order'].default_get(['order_policy'])
        return default_dict.get('order_policy')

    @api.model
    def _get_selection_invoice_state(self):
        return self.env['stock.picking'].fields_get(
            allfields=['invoice_state'])['invoice_state']['selection']

    def default_invoice_state(self):
        default_dict = self.env['stock.picking'].default_get(['invoice_state'])
        return default_dict.get('invoice_state')

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Entry Sequence', copy=False,
        domain=_get_domain_sequence_id)
    journal_id = fields.Many2one(
        comodel_name='account.journal', string='Billing Journal',
        domain=[('type', '=', 'sale')])
    refund_journal_id = fields.Many2one(
        comodel_name='account.journal', string='Refund Billing Journal',
        domain=[('type', '=', 'sale_refund')])
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse', required=True)
    picking_policy = fields.Selection(
        selection='_get_selection_picking_policy', string='Shipping Policy',
        required=True, default=default_picking_policy)
    order_policy = fields.Selection(
        selection='_get_selection_order_policy', string='Create Invoice',
        required=True, default=default_order_policy)
    invoice_state = fields.Selection(
        selection='_get_selection_invoice_state', string='Invoice Control',
        required=True, default=default_invoice_state)
