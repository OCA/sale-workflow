# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Rental module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class create_rental_product(orm.TransientModel):
    _name = 'create.rental.product'
    _description = 'Create the Rental Service Product'

    _columns = {
        'sale_price_per_day': fields.float(
            'Sale Price per Day', required=True,
            digits_compute=dp.get_precision('Product Price')),
        # I would like to translate the field 'name_prefix', but
        # it doesn't seem to work in a wizard
        'name_prefix': fields.char(
            'Product Name Prefix', size=64, required=True),
        'default_code_prefix': fields.char(
            'Prefix for Default Code', size=16, required=True),
        'categ_id': fields.many2one(
            'product.category', 'Product Category', required=True),
        }

    _defaults = {
        'sale_price_per_day': 1.0,
        'default_code_prefix': 'RENT-',
        'name_prefix': 'Rental of one ',
    }

    def create_rental_product(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Only 1 ID'
        if context is None:
            context = {}
        #  check that a rental product doesn't already exists ?
        hw_product_id = context.get('active_id')
        pp_obj = self.pool['product.product']
        hw_product = pp_obj.browse(cr, uid, hw_product_id, context=context)
        assert isinstance(hw_product_id, int), 'Active ID is not set'
        wiz = self.browse(cr, uid, ids[0], context=context)
        (uom_model, day_uom_id) = self.pool['ir.model.data'].\
            get_object_reference(cr, uid, 'product', 'product_uom_day')
        assert uom_model == 'product.uom', 'Must be product.uom'

        product_id = pp_obj.create(cr, uid, {
            'type': 'service',
            'sale_ok': True,
            'purchase_ok': False,
            'uom_id': day_uom_id,
            'uom_po_id': day_uom_id,
            'list_price': wiz.sale_price_per_day,
            'name': '%s%s' % (
                wiz.name_prefix and wiz.name_prefix + ' ' or '',
                hw_product.name),
            'default_code': '%s%s' % (
                wiz.default_code_prefix or '',
                hw_product.default_code),
            'rented_product_id': hw_product_id,
            'must_have_dates': True,
            'categ_id': wiz.categ_id.id,
            }, context=context)

#        lang_ids = self.pool['res.lang'].search(cr, uid, [], context=context)
#        for lang in self.pool['res.lang'].browse(
#                cr, uid, lang_ids, context=context):
#            ctx_lang = context.copy()
#            ctx_lang['lang'] = ctx_lang.code
#            wiz_lang = self.browse(cr, uid, ids[0], context=ctx_lang)
#            pp_obj.write(cr, uid, product_id, {
#                'name': '%s%s' % (
#                    wiz.name_prefix and wiz.name_prefix + ' ' or '',
#                    hw_product.name),
#                }, context=ctx_lang)
        return {
            'name': pp_obj._description,
            'type': 'ir.actions.act_window',
            'res_model': pp_obj._name,
            'view_type': 'form',
            'view_mode': 'form,tree,kanban',
            'nodestroy': False,  # Close the wizard pop-up
            'target': 'current',
            'res_id': product_id,
            }
