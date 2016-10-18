# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Yannick Vaucher
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp.tests.common import TransactionCase


class TestSaleIsDelivered(TransactionCase):
    """Check the _get_shipped method of Sale Order. """

    def test_sale_no_proc(self):
        """False when no procurement on both sale.order.line"""
        self.assertFalse(self.sale.shipped)

    def test_sale_no_proc_one_service(self):
        """False when, no procurement on both line but one is service"""
        self.sale_line1.product_id = self.service_product
        self.assertFalse(self.sale.shipped)

    def test_sale_no_proc_all_services(self):
        """True when, no procurement on both lines but both are services"""
        self.sale_line1.product_id = self.service_product
        self.sale_line2.product_id = self.service_product
        self.assertTrue(self.sale.shipped)

    def test_sale_not_all_proc(self):
        """False, when one line with and one without procurement done"""
        self.sale_line1.procurement_group_id = self.proc_group1
        self.proc1.state = 'done'

        self.assertFalse(self.sale.shipped)

    def test_sale_proc_and_service(self):
        """True when, one line with procurement done and one line for service
        """
        self.sale_line1.procurement_group_id = self.proc_group1
        self.proc1.state = 'done'
        self.sale_line2.product_id = self.service_product

        self.assertTrue(self.sale.shipped)

    def test_sale_partially_delivered(self):
        """False when, all lines with procurement, one is partially delivered
        """
        self.sale_line1.procurement_group_id = self.proc_group1
        self.sale_line2.procurement_group_id = self.proc_group2
        self.proc1.state = 'done'
        self.proc2.state = 'running'

        self.assertFalse(self.sale.shipped)

    def test_sale_is_delivered(self):
        """True, when both line have a done procurement"""
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
        Product = self.env['product.product']
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

        self.service_product = Product.new({'type': 'service'})
