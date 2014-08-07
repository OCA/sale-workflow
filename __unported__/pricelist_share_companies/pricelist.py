# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2011 Camptocamp SA
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
from openerp.osv import orm, fields


class PriceType(orm.Model):
    _inherit = 'product.price.type'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }

    def _check_unicity_per_company(self, cr, uid, ids, context=None):
        for price_type in self.browse(cr, uid, ids, context=context):
            if price_type.company_id:
                cr.execute(
                    'SELECT id FROM product_price_type WHERE id != %s AND '
                    'field = %s and company_id = %s',
                    (price_type.id, price_type.field, price_type.company_id.id)
                )
                res = cr.fetchall()
                if res:
                    return False
        return True

    _constraints = [
        (_check_unicity_per_company,
         'You can not create two price types with same field and same '
         'company.', ['company_id', 'field']),
    ]

    def search(
        self, cr, uid, args, offset=0, limit=None, order=None, context=None,
        count=False
    ):
        """ Inherit the default search of price types to replace search of
        list_price and standard_price by another field according to company
        This is useful to create a field on the product, for example
        list_price_company_x, which is the price of the product for the
        company_x.
        In the configuration of the company, choose to use this field instead
        of the list_price, this method will now return the good list_price
        according to the setup"""

        def replace_args(search_args, ptype, company):
            if not filter(lambda x: x[2] == ptype, search_args):
                return search_args

            if getattr(company, "%s_field" % ptype):
                operator = filter(lambda x: x[0] == 'field', search_args)[0][1]
                value = filter(lambda x: x[0] == 'field', search_args)[0][2]
                # get the other arguments of the search
                search_args = filter(lambda x: x[0] != 'field', search_args)
                # replace the price list by the one configured on the company
                search_args += [
                    ('field', operator, getattr(company, "%s_field" % value))]
            return search_args

        args1 = args[:]
        if filter(
            lambda x: x[0] == 'field' and x[2] == 'standard_price', args
        ):
            company = self.pool.get('res.users').browse(
                cr, uid, uid).company_id
            args1 = replace_args(args1, 'standard_price', company)

        return super(PriceType, self).search(
            cr, uid, args1, offset, limit, order, context=context, count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
