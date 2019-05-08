# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_customer_code = fields.Char(
        compute='_compute_product_customer_code',
        string='Product Customer Code',
    )

    @api.multi
    @api.depends('product_id')
    def _compute_product_customer_code(self):
        for line in self.filtered(lambda sol: sol.product_id.customer_ids):
            supplierinfo = self.get_customer_supplierinfo(line)
            line.product_customer_code = supplierinfo.product_code

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        for line in self.filtered(
                lambda sol: sol.product_id.product_tmpl_id.customer_ids and
                sol.order_id.pricelist_id.item_ids):
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
                supplierinfo = self.get_customer_supplierinfo(line)
                if supplierinfo and supplierinfo.min_qty:
                    line.product_uom_qty = supplierinfo.min_qty
        return result

    def _supplierinfo_domain(self, line):
        """Common domain for product templates and variants"""
        return [
            ('supplierinfo_type', '=', 'customer'),
            ('name', '=', line.order_partner_id.id),
        ]

    def get_customer_supplierinfo(self, line):
        """
        Search supplierinfo for variant first, if it has not been found then
        search by product template
        """
        supplierinfo = self.env['product.supplierinfo'].search(
            self._supplierinfo_domain(line) +
            [
                '|',
                ('product_id', '=', line.product_id.id),
                '&',
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('product_id', '=', False),
            ],
            limit=1,
            order='product_id, sequence, min_qty desc, price')
        return supplierinfo
