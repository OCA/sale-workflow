# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Rental module for Odoo
#    Copyright (C) 2014-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class CreateRentalProduct(models.TransientModel):
    _name = 'create.rental.product'
    _description = 'Create the Rental Service Product'

    @api.model
    def _default_name(self):
        assert self.env.context.get('active_model') == 'product.product',\
            'Wrong underlying model, should be product.product'
        hw_product = self.env['product.product'].browse(
            self.env.context['active_id'])
        return _('Rental of a %s') % hw_product.name

    @api.model
    def _default_code(self):
        assert self.env.context.get('active_model') == 'product.product',\
            'Wrong underlying model, should be product.product'
        hw_product = self.env['product.product'].browse(
            self.env.context['active_id'])
        return _('RENT-%s') % hw_product.default_code

    sale_price_per_day = fields.Float(
        string='Rental Price per Day', required=True,
        digits=dp.get_precision('Product Price'), default=1.0)
    name = fields.Char(
        string='Product Name', size=64, required=True,
        default=_default_name)
    default_code = fields.Char(
        string='Default Code', size=16, required=True,
        default=_default_code)
    categ_id = fields.Many2one(
        'product.category', string='Product Category', required=True)

    @api.multi
    def create_rental_product(self):
        self.ensure_one()
        #  check that a rental product doesn't already exists ?
        assert self.env.context.get('active_model') == 'product.product',\
            'Wrong underlying model, should be product.product'
        hw_product_id = self.env.context.get('active_id')
        assert hw_product_id, 'Active ID is not set'
        pp_obj = self.env['product.product']
        day_uom_id = self.env.ref('product.product_uom_day').id

        product = pp_obj.create({
            'type': 'service',
            'sale_ok': True,
            'purchase_ok': False,
            'uom_id': day_uom_id,
            'uom_po_id': day_uom_id,
            'list_price': self.sale_price_per_day,
            'name': self.name,
            'default_code': self.default_code,
            'rented_product_id': hw_product_id,
            'must_have_dates': True,
            'categ_id': self.categ_id.id,
            })

        action = {
            'name': pp_obj._description,
            'type': 'ir.actions.act_window',
            'res_model': pp_obj._name,
            'view_mode': 'form,tree,kanban',
            'nodestroy': False,  # Close the wizard pop-up
            'target': 'current',
            'res_id': product.id,
            }
        return action
