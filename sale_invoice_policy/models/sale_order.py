# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities')],
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        help='Ordered Quantity: Invoice based on the quantity the customer '
             'ordered.\n'
             'Delivered Quantity: Invoiced based on the quantity the vendor '
             'delivered (time or deliveries).')
    invoice_policy_required = fields.Boolean(
        compute='_compute_invoice_policy_required',
        default=lambda self: self.env['ir.values'].get_default(
            'sale.config.settings', 'sale_invoice_policy_required'),
    )

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrder, self).default_get(fields_list)
        default_sale_invoice_policy = self.env['ir.values'].get_default(
            'sale.config.settings', 'sale_default_invoice_policy')
        if 'invoice_policy' not in res:
            res.update({
                'invoice_policy': default_sale_invoice_policy
            })
        return res

    @api.multi
    @api.depends()
    def _compute_invoice_policy_required(self):
        invoice_policy_required = self.env['ir.values'].get_default(
            'sale.config.settings', 'sale_invoice_policy_required')
        for sale in self:
            sale.invoice_policy_required = invoice_policy_required
