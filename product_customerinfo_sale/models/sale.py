# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('product_id')
    def _compute_get_product_customer_code(self):
        for line in self.filtered(
                lambda sol: sol.product_id.product_tmpl_id.customer_ids):
            product = line.product_id
            code_id = self.env['product.supplierinfo'].search([
                '|', ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('product_id', '=', product.id),
                ('supplierinfo_type', '=', 'customer'),
                ('name', '=', line.order_id.partner_id.id),
            ], limit=1)
            line.product_customer_code = code_id.product_code or ''
            if code_id.product_name:
                line.name = code_id.product_name

    product_customer_code = fields.Char(
        compute='_compute_get_product_customer_code',
        string='Product Customer Code',
        size=64
    )

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        for line in self.filtered(
                lambda sol: sol.product_id.product_tmpl_id.customer_ids
                and sol.order_id.pricelist_id.item_ids):
            product = line.product_id
            items = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', line.order_id.pricelist_id.id),
                ('compute_price', '=', 'formula'), ('base', '=', 'partner'),
                '|', ('applied_on', '=', '3_global'),
                '|', '&', ('categ_id', '=', product.categ_id.id),
                ('applied_on', '=', '2_product_category'), '|',
                '&', ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('applied_on', '=', '1_product'), '&',
                ('product_id', '=', product.id),
                ('applied_on', '=', '0_product_variant'),
            ])
            if items:
                code_id = self.env['product.supplierinfo'].search([
                    '|', ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('product_id', '=', product.id),
                    ('supplierinfo_type', '=', 'customer'),
                    ('name', '=', line.order_id.partner_id.id),
                ], limit=1)
                if code_id and code_id.min_qty:
                    line.product_uom_qty = code_id.min_qty
        return result
