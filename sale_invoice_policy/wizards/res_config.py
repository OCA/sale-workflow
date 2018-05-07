# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class SaleConfigSettings(models.TransientModel):

    _name = 'sale.config.settings'
    _inherit = 'sale.config.settings'

    sale_default_invoice_policy = fields.Selection(
        selection=[
            ('order', 'Ordered quantities'),
            ('delivery', 'Delivered quantities')
        ],
        related='default_invoice_policy',
        readonly=True,
    )
    sale_invoice_policy_required = fields.Boolean(
        help="This makes Invoice Policy required on Sale Orders"
    )

    @api.multi
    def set_default_sale_default_invoice_policy(self):
        """
        Set value in an ir_value but get default from the related
        :return:
        """
        ir_values_obj = self.env['ir.values']
        if self.env['res.users'].has_group('base.group_erp_manager'):
            ir_values_obj = ir_values_obj.sudo()
            ir_values_obj.set_default(
                'sale.config.settings',
                'sale_default_invoice_policy',
                self.sale_default_invoice_policy
            )

    @api.model
    def get_default_sale_invoice_policy_required(self, fields_list):
        return {
            'sale_invoice_policy_required': self.env['ir.values'].get_default(
                'sale.config.settings', 'sale_invoice_policy_required')
        }

    @api.multi
    def set_default_sale_invoice_policy_required(self):
        ir_values_obj = self.env['ir.values']
        if self.env['res.users'].has_group('base.group_erp_manager'):
            ir_values_obj = ir_values_obj.sudo()
            ir_values_obj.set_default(
                'sale.config.settings',
                'sale_invoice_policy_required',
                self.sale_invoice_policy_required
            )
