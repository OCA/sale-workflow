# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    bom_with_option = fields.Boolean(compute='_compute_bom_with_option')
    component_of_product_ids = fields.Many2many(
        comodel_name='product.product',
        compute='_compute_component_of_product_ids',
        search='_search_component_of_product_ids')

    def _bom_find(self):
        self.ensure_one()
        return self.env['mrp.bom']._bom_find(product=self)

    def _compute_bom_with_option(self):
        for record in self:
            bom = record._bom_find()
            record.bom_with_option = bom.with_option

    def _compute_component_of_product_ids(self):
        for record in self:
            bom_lines = self.env['mrp.bom.line'].search([
                ('product_id', '=', record.id)
                ])
            products = self.env['product.product'].browse(False)
            for bom_line in bom_lines:
                if bom_line.bom_id.product_id:
                    products |= bom_line.bom_id.product_id
                else:
                    products |=\
                        bom_line.bom_id.product_tmpl_id.product_variant_ids
            record.component_of_product_ids = products.ids

    def _search_component_of_product_ids(self, operator, value):
        if operator != '=':
            raise UserError(_("Operator %s not supported") % operator)
        else:
            product = self.env['product.product'].browse(value)
            bom = product._bom_find()
            return [('id', 'in', bom.mapped('bom_line_ids.product_id').ids)]
