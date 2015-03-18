# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
#    Copyright 2014 Camptocamp SA
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
from openerp.tests import common


class TestConsigneeSaleOrder(common.TransactionCase):
    """ Test origin address is correctly set on picking
    """

    def setUp(self):
        super(TestConsigneeSaleOrder, self).setUp()

        model_data = self.env['ir.model.data']
        ref = model_data.xmlid_to_res_id

        part1_id = ref('base.res_partner_1')
        part12_id = ref('base.res_partner_12')

        SO = self.env['sale.order']
        SOL = self.env['sale.order.line']

        so_vals = {
            'partner_id': part12_id,
            'consignee_id': part1_id,
            }

        res = SO.onchange_partner_id(part12_id)
        so_vals.update(res['value'])

        self.so = SO.create(so_vals)

        # sale exceptions, if installed, is irrelevant here. If it isn't this
        # is no-op
        self.so.ignore_exceptions = True

        sol_vals = {
            'order_id': self.so.id,
            'product_id': ref('product.product_product_33'),
            'name': "[HEAD-USB] Headset USB",
            'product_uom_qty': 24,
            'product_uom': ref('product.product_uom_unit'),
            'price_unit': 65,
            }
        SOL.create(sol_vals)

    def test_create_picking_from_so(self):
        """Create a picking in from purchase order and check
        consignee is copied

        """
        self.so.signal_workflow('order_confirm')

        self.assertEquals(self.so.picking_ids.consignee_id,
                          self.so.consignee_id)
