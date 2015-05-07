# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.osv import fields, orm


class SaleOrderLine(orm.Model):

    """Adds an exception function to be called by the sale_exceptions module.

    The function will ensure that the discount of the line does not exceed
    the maximum discount defined for the product.

    """

    _inherit = "sale.order.line"

    def _should_skip_discount_checks(self, cr, uid, line_br, context=None):

        if (
            line_br.product_id and
            line_br.product_id.has_max_sale_discount
        ):
            return False
        else:
            return True

    def discount_exceeds_max(self, cr, uid, l_id, context=None):
        """Predicate that checks whether a SO line has a discount that
        exceeds the maximum discount defined in the product.

        :return: True if the discount of the line is equal or less than the
        one defined in the product, or if the line contains no product.

        """
        if context is None:
            context = {}
        if isinstance(l_id, (tuple, list)):
            assert len(l_id) == 1, "Only one id supported"
            l_id = l_id[0]
        line = self.browse(cr, uid, l_id, context=context)

        if self._should_skip_discount_checks(cr, uid, line, context=context):
            return True

        max_discount = line.product_id.max_sale_discount

        if line.discount > max_discount:
            return False
        return True
