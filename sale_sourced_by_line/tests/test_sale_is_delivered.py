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
from openerp.tests.common import TransactionCase


class TestSaleIsDelivered(TransactionCase):
    """Check the _get_shipped method of Sale Order. """

    def test_sale_no_proc(self):
        self.assertFalse(self.sale.shipped)

    def test_sale_not_all_proc(self):
        self.sale_line1.procurement_group_id = self.proc_group1
        self.proc1.state = 'done'

        self.assertFalse(self.sale.shipped)

    def test_sale_partially_delivered(self):
        self.sale_line1.procurement_group_id = self.proc_group1
        self.sale_line2.procurement_group_id = self.proc_group2
        self.proc1.state = 'done'
        self.proc2.state = 'running'

        self.assertFalse(self.sale.shipped)

    def test_sale_is_delivered(self):
        self.sale_line1.procurement_group_id = self.proc_group1
        self.sale_line2.procurement_group_id = self.proc_group2
        self.proc1.state = 'done'
        self.proc2.state = 'done'

        self.assertTrue(self.sale.shipped)

    def setUp(self):
        """Setup a Sale Order with 2 lines.
        And prepare procurements

        I use Model.new to get a model instance that is not saved to the
        database, but has working methods.

        """
        super(TestSaleIsDelivered, self).setUp()
        SO = self.env['sale.order']
        SOL = self.env['sale.order.line']
        Procurement = self.env['procurement.order']
        ProcurementGroup = self.env['procurement.group']
        self.sale = SO.new()
        self.sale_line1 = SOL.new()
        self.sale_line2 = SOL.new()
        self.sale_line1.order_id = self.sale
        self.sale_line2.order_id = self.sale

        self.sale.order_line = SOL.browse([self.sale_line1.id,
                                           self.sale_line2.id])

        self.proc1 = Procurement.new()
        self.proc_group1 = ProcurementGroup.new()
        self.proc_group1.procurement_ids = self.proc1

        self.proc2 = Procurement.new()
        self.proc_group2 = ProcurementGroup.new()
        self.proc_group2.procurement_ids = self.proc2
