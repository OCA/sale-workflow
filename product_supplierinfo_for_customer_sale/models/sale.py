# -*- coding: utf-8 -*-
# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _compute_get_product_customer_code(self):
        product_supplierinfo_obj = self.env['product.supplierinfo']
        for line in self.filtered(lambda sol: sol.product_id.supplier_ids):
            product = line.product_id
            code_id = product_supplierinfo_obj.search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('type', '=', 'customer'),
                ('name', '=', line.order_id.partner_id.id),
            ], limit=1)
            line.product_customer_code = code_id.product_code or ''

    product_customer_code = fields.Char(
        compute='_compute_get_product_customer_code',
        string='Product Customer Code',
        size=64
    )
