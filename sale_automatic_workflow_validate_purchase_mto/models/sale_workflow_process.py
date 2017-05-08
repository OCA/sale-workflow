# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleWorkflowProcess(models.Model):

    _inherit = 'sale.workflow.process'

    validate_purchase_mto = fields.Boolean(
        string='Validate Purchase Orders MTO',
        help='Select this to validate purchase orders that are generated'
        'directly by sale orders')
    purchase_order_mto_domain = fields.Char(
        string='Purchase Order Domain',
        default="[('state', '=', 'sale')]"
        )
    purchase_order_mto_filter_id = fields.Many2one(
        'ir.filters',
        string='Validate Purchase Order MTO Filter',
        default=lambda self: self._default_filter(
            'sale_automatic_workflow_validate_purchase_mto'
            '.automatic_workflow_po_mto_filter'
        )
    )
    purchase_order_mto_purchase_domain = fields.Char(
        string='Purchase Order Domain',
        default="[('state', 'not in', ['purchase','done','cancel'])]"
        )
    purchase_order_mto_purchase_filter_id = fields.Many2one(
        'ir.filters',
        string='Validate Purchase Order MTO Filter',
        default=lambda self: self._default_filter(
            'sale_automatic_workflow_validate_purchase_mto.'
            'automatic_workflow_po_mto_purchase_filter'
        )
    )

    @api.onchange('purchase_order_mto_filter_id')
    def _onchange_purchase_order_mto_filter_id(self):
        if self.purchase_order_mto_filter_id:
            self.purchase_order_mto_domain =\
                self.purchase_order_mto_filter_id.domain

    @api.onchange('purchase_order_mto_purchase_filter_id')
    def _onchange_purchase_order_mto_purchase_filter_id(self):
        if self.purchase_order_mto_filter_id:
            self.purchase_order_mto_purchase_domain = \
                self.purchase_order_mto_purchase_filter_id.domain
