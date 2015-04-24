# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
#    Copyright 2015 Camptocamp SA
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
import openerp.tests.common as test_common
from openerp import fields


class TestProcurementGroup(test_common.TransactionCase):

    def test_sourced_by_no_po(self):
        """ Test it creates only one Procurement Group if not sourced

        Procurement Group will be named after sale's name
        """
        so_line = self.env['sale.order.line'].create({
            'order_id': self.sale.id,
            'name': 'Line',  # required
            'price_unit': 99,  # required
            # no sourced_by
        })

        self.sale.action_ship_create()

        self.assertTrue(so_line.procurement_group_id)
        self.assertEqual(so_line.procurement_group_id.name,
                         self.sale.name)

    def test_all_sourced_by_a_single_po(self):
        """ Test it creates only one Procurement Group if same PO on all lines

        Procurement Group will be named after sale and purchase names
        """
        so_line1 = self.env['sale.order.line'].create({
            'order_id': self.sale.id,
            'sourced_by': self.po1_line1.id,
            'name': 'Line1',  # required
            'price_unit': 99,  # required
        })
        so_line2 = self.env['sale.order.line'].create({
            'order_id': self.sale.id,
            'sourced_by': self.po1_line2.id,
            'name': 'Line2',  # required
            'price_unit': 99,  # required
        })

        self.sale.action_ship_create()

        self.assertTrue(so_line1.procurement_group_id)
        self.assertTrue(so_line2.procurement_group_id)
        # Ensure we only one procurement group
        self.assertEqual(so_line1.procurement_group_id,
                         so_line2.procurement_group_id)
        self.assertEqual(
            so_line1.procurement_group_id.name,
            self.sale.name + '/' + self.po1.name
        )

    def test_sourced_by_multiple_po(self):
        """ Test it creates one Procurement Group per PO """
        so_line1 = self.env['sale.order.line'].create({
            'order_id': self.sale.id,
            'sourced_by': self.po1_line1.id,
            'name': 'Line1',  # required
            'price_unit': 99,  # required
        })
        so_line2 = self.env['sale.order.line'].create({
            'order_id': self.sale.id,
            'sourced_by': self.po2_line.id,
            'name': 'Line2',  # required
            'price_unit': 99,  # required
        })

        self.sale.action_ship_create()

        self.assertTrue(so_line1.procurement_group_id)
        self.assertTrue(so_line2.procurement_group_id)
        # Ensure we have 2 different procurement groups
        self.assertNotEqual(so_line1.procurement_group_id,
                            so_line2.procurement_group_id)
        self.assertEqual(
            so_line1.procurement_group_id.name,
            self.sale.name + '/' + self.po1.name
        )
        self.assertEqual(
            so_line2.procurement_group_id.name,
            self.sale.name + '/' + self.po2.name
        )

    def setUp(self):
        super(TestProcurementGroup, self).setUp()
        self.po1 = self.env['purchase.order'].create({
            'name': 'PO1',
            'partner_id': self.ref('base.res_partner_2'),  # required
            'location_id': self.ref('stock.stock_location_stock'),  # required
            'pricelist_id': 1,  # required
        })
        self.po2 = self.env['purchase.order'].create({
            'name': 'PO2',
            'partner_id': self.ref('base.res_partner_2'),  # required
            'location_id': self.ref('stock.stock_location_stock'),  # required
            'pricelist_id': 1,  # required
        })
        self.po1_line1 = self.env['purchase.order.line'].create({
            'name': 'PO1L1',  # required
            'partner_id': self.ref('base.res_partner_2'),  # required
            'order_id': self.po1.id,
            'price_unit': 99,  # required
            'date_planned': fields.Datetime.now(),  # required
        })
        self.po1_line2 = self.env['purchase.order.line'].create({
            'name': 'PO1L2',  # required
            'order_id': self.po1.id,
            'price_unit': 99,  # required
            'date_planned': fields.Datetime.now(),  # required
        })
        self.po2_line = self.env['purchase.order.line'].create({
            'name': 'PO2L1',  # required
            'order_id': self.po2.id,
            'price_unit': 99,  # required
            'date_planned': fields.Datetime.now(),  # required
        })
        self.sale = self.env['sale.order'].create({
            'name': 'SO1',
            'partner_id': self.ref('base.res_partner_12'),  # required
        })
