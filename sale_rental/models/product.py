# -*- coding: utf-8 -*-
# Copyright 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
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
        for product in self:
            if product.rented_product_id and product.type != 'service':
                raise ValidationError(_(
                    "The rental product '%s' must be of type 'Service'.")
                    % product.name)
            if product.rented_product_id and not product.must_have_dates:
                raise ValidationError(_(
                    "The rental product '%s' must have the option "
                    "'Must Have Start and End Dates' checked.")
                    % product.name)
            # In the future, we would like to support all time UoMs
            # but it is more complex and requires additionnal developments
            day_uom = product.env.ref('product.product_uom_day')
            if product.rented_product_id and product.uom_id != day_uom:
                raise ValidationError(_(
                    "The unit of measure of the rental product '%s' must "
                    "be 'Day'.") % product.name)

    @api.multi
    def _need_procurement(self):
        # Missing self.ensure_one() in the native code !
        res = super(ProductProduct, self)._need_procurement()
        if not res:
            for product in self:
                if product.type == 'service' and product.rented_product_id:
                    return True
        # TODO find a replacement for soline.rental_type == 'new_rental')
        return res
