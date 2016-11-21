# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import api, fields, models


class SaleOrderTypology(models.Model):
    _name = 'sale.order.type'
    _description = 'Type of sale order'

    @api.model
    def _get_selection_picking_policy(self):
        return self.env['sale.order'].fields_get(
            allfields=['picking_policy'])['picking_policy']['selection']

    def default_picking_policy(self):
        default_dict = self.env['sale.order'].default_get(['picking_policy'])
        return default_dict.get('picking_policy')

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Entry Sequence', copy=False)
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
