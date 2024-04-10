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

from openerp import models, fields


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_use_product_description_per_so_line = fields.Boolean(
        "Allow using only the product sale description on the sales order "
        "lines", implied_group="sale_order_line_description."
        "group_use_product_description_per_so_line",
        help="Allows you to use only product sale description on the "
        "sales order line."
        )
