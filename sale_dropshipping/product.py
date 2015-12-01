# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Akretion LDTA (<http://www.akretion.com>).
#    @author Raphaël Valyi
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
#
from openerp.osv import fields, orm


class product_supplierinfo(orm.Model):

    _inherit = "product.supplierinfo"

    _columns = {
        "direct_delivery_flag": fields.boolean('Drop Shipping?'),
    }

product_supplierinfo()


class product_product(orm.Model):

    _inherit = "product.product"

    def _is_direct_delivery_from_product(
        self, cr, uid, ids, name, arg, context=None
    ):
        res = {}

        def is_direct_delivery_from_suppliers(product):
            cr.execute(
                """SELECT direct_delivery_flag FROM product_supplierinfo
                INNER JOIN res_partner
                    ON product_supplierinfo.name = res_partner.id
                WHERE product_id=%s
                AND active=true ORDER BY sequence ASC LIMIT 1;""",
                (product.product_tmpl_id.id,))
            result = cr.fetchone()
            if result and result[0]:
                return True
            return False

        for product in self.browse(cr, uid, ids):
            if product.procure_method == 'make_to_order':
                res[product.id] = is_direct_delivery_from_suppliers(product)
            elif 'qty' in context:
                # TODO deal with partial availability?
                if product.virtual_available < context['qty']:
                    res[product.id] = is_direct_delivery_from_suppliers(
                        product)
                else:  # Available in stock
                    res[product.id] = False
            else:  # No quantity mentioned so we answer for 'any' quantity
                res[product.id] = is_direct_delivery_from_suppliers(product)
        return res

    _columns = {
        'is_direct_delivery_from_product': fields.function(
            _is_direct_delivery_from_product,
            method=True,
            type='boolean',
            string="Is Supplier Direct Delivery Automatic?")
    }
