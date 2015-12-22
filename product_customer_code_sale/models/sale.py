# -*- coding: utf-8 -*-
# Copyright 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'order_id.partner_id')
    def _get_product_customer_code(self):
        product_customer_code_obj = self.env['product.customer.code']
        for line in self:
            partner = line.order_id.partner_id
            product = line.product_id
            if product and partner:
                code_ids = product_customer_code_obj.search([
                    ('product_id', '=', product.id),
                    ('partner_id', '=', partner.id),
                ], limit=1)
                if code_ids:
                    line.product_customer_code = code_ids[0].product_code or ''


    product_customer_code = fields.Char(string='Product Customer Code',
        compute='_get_product_customer_code', size=64)
