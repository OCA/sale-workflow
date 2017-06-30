# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) info@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        res = super(ProductProduct, self).name_search(
            name, args=args, operator=operator, limit=limit)
        if (not name or not self._context.get('partner_id') or
                len(res) >= limit):
            return res
        partner_id = self._context['partner_id']
        limit -= len(res)
        supplierinfo = self.env['product.supplierinfo'].search(
            [('name', '=', partner_id), '|', ('product_code', operator, name),
             ('product_name', operator, name)], limit=limit)
        if not supplierinfo:
            return res
        res_template_ids = self.browse(
            [product_id for product_id, _name in res]).mapped(
                'product_tmpl_id')
        product_tmpl_ids = (supplierinfo.mapped('product_tmpl_id') -
                            res_template_ids)
        product = self.search(
            [('product_tmpl_id', 'in', product_tmpl_ids.ids)], limit=limit)
        res.extend(product.name_get())
        return res
