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

from openerp import models, fields, api, exceptions, _
from openerp.tools.translate import _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def check_discount_limit(self):
        model_data_obj = self.env['ir.model.data']
        res_groups_obj = self.env['res.groups']
        xml_id = model_data_obj._get_id('sale_discount_limit',
                                        'group_so_discount_block_releaser')
        group_user_ids = []
        if xml_id:
            group_releaser_model = model_data_obj.browse(xml_id)
            group_releaser_id = group_releaser_model.res_id
            group_releaser = res_groups_obj.browse(group_releaser_id)
            group_user_ids = [user.id for user
                              in group_releaser.users]
        for order in self:
            for line in order.order_line:
                max_discount = 0.0
                if line.product_id:
                    max_discount = line.product_id.max_sale_discount
                if line.product_id and line.discount > max_discount \
                        and self.env.uid not in group_user_ids:
                    raise exceptions.Warning(
                        _('Maximum permitted discount exceeded.'),
                        _("Cannot confirm the quotation. The maximum allowed "
                          "discount for '%s' is %s %%. Only a user "
                          "that belongs to group 'Sales Quotation Discount "
                          "Block Releaser' can approve the quotation.")
                        % (line.name, max_discount))
        return True
