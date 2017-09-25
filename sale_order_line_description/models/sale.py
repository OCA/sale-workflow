# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2013-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            if self.user_has_groups(
                    'sale_order_line_description.'
                    'group_use_product_description_per_so_line'):
                product = self.product_id.with_context(
                    lang=self.order_id.partner_id.lang,
                )
                if product.description_sale:
                    vals = {'name': product.description_sale}
                    self.update(vals)

        return res
