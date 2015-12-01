# -*- coding: utf-8 -*-
#
#
#    Sale Fiscal Position Update module for OpenERP
#    Copyright (C) 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Mathieu Vatel <mathieu _at_ julius.fr>
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
#

from openerp.osv import orm
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = "sale.order"

    def fiscal_position_change(
            self, cr, uid, ids, fiscal_position, order_line,
            context=None):
        '''Function executed by the on_change on the fiscal_position field
        of a sale order ; it updates taxes on all order lines'''
        assert len(ids) in (0, 1), 'One ID max'
        fp_obj = self.pool['account.fiscal.position']
        res = {}
        line_dict = self.resolve_2many_commands(
            cr, uid, 'order_line', order_line, context=context)
        lines_without_product = []
        if fiscal_position:
            fp = fp_obj.browse(cr, uid, fiscal_position, context=context)
        else:
            fp = False
        for line in line_dict:
            # Reformat line_dict so as to be compatible with what is
            # accepted in res['value']
            for key, value in line.iteritems():
                if isinstance(value, tuple) and len(value) == 2:
                    line[key] = value[0]
            if line.get('product_id'):
                product = self.pool['product.product'].browse(
                    cr, uid, line.get('product_id'), context=context)
                taxes = product.taxes_id
                tax_ids = fp_obj.map_tax(
                    cr, uid, fp, taxes, context=context)

                line['tax_id'] = [(6, 0, tax_ids)]
            else:
                lines_without_product.append(line.get('name'))
        res['value'] = {}
        res['value']['order_line'] = line_dict

        if lines_without_product:
            res['warning'] = {'title': _('Warning')}
            if len(lines_without_product) == len(line_dict):
                res['warning']['message'] = _(
                    "The Sale Order Lines were not updated to the new "
                    "Fiscal Position because they don't have Products.\n"
                    "You should update the Taxes of each "
                    "Sale Order Line manually.")
            else:
                display_line_names = ''
                for name in lines_without_product:
                    display_line_names += "- %s\n" % name
                res['warning']['message'] = _(
                    "The following Sale Order Lines were not updated "
                    "to the new Fiscal Position because they don't have a "
                    "Product:\n %s\nYou should update the "
                    "Taxes of these Sale Order Lines manually."
                ) % display_line_names,
        return res
