# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Link rental service -> rented HW product
    rented_product_id = fields.Many2one(
        'product.product', string='Related Rented Product',
        domain=[('type', 'in', ('product', 'consu'))])
    # Link rented HW product -> rental service
    rental_service_ids = fields.One2many(
        'product.product', 'rented_product_id',
        string='Related Rental Services')

    @api.constrains('rented_product_id', 'must_have_dates', 'type', 'uom_id')
    def _check_rental(self):
        day_uom = self.env.ref('uom.product_uom_day')
        for product in self:
            if product.rented_product_id:
                if product.type != 'service':
                    raise ValidationError(_(
                        "The rental product '%s' must be of type 'Service'.")
                        % product.name)
                if not product.must_have_dates:
                    raise ValidationError(_(
                        "The rental product '%s' must have the option "
                        "'Must Have Start and End Dates' checked.")
                        % product.name)
                # In the future, we would like to support all time UoMs
                # but it is more complex and requires additionnal developments
                if product.uom_id != day_uom:
                    raise ValidationError(_(
                        "The unit of measure of the rental product '%s' must "
                        "be 'Day'.") % product.name)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rented_product_tmpl_id = fields.Many2one(
        'product.template', compute='_compute_rented_product_tmpl_id',
        string='Rented Product',
        inverse='_set_rented_product_tmpl_id', store=True)
    rental_service_tmpl_ids = fields.One2many(
        'product.template', 'rented_product_tmpl_id',
        string='Rental Services')

    @api.depends('product_variant_ids', 'product_variant_ids.rented_product_id')
    def _compute_rented_product_tmpl_id(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.rented_product_tmpl_id = template.product_variant_ids.rented_product_id.product_tmpl_id.id
        for template in (self - unique_variants):
            template.rented_product_tmpl_id = False

    def _set_rented_product_tmpl_id(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.rented_product_id = template.rented_product_tmpl_id.product_variant_ids[0].id
