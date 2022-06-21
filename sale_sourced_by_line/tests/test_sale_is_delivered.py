# Copyright 2014 Camptocamp SA - Yannick Vaucher
# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


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
        self.proc1.state = "done"

        self.assertFalse(self.sale.shipped)

    def test_sale_proc_and_service(self):
        """True when, one line with procurement done and one line for service
        """
        self.sale_line1.procurement_group_id = self.proc_group1
        self.proc1.state = "done"
        self.sale_line2.product_id = self.service_product

        self.assertTrue(self.sale.shipped)

    def test_sale_partially_delivered(self):
        """False when, all lines with procurement, one is partially delivered
        """
        self.sale_line1.procurement_group_id = self.proc_group1
        self.sale_line2.procurement_group_id = self.proc_group2
        self.proc1.state = "done"
        self.proc2.state = "running"

        self.assertFalse(self.sale.shipped)

    def test_sale_is_delivered(self):
        """True, when both line have a done procurement"""
        self.sale_line1.procurement_group_id = self.proc_group1
        self.sale_line2.procurement_group_id = self.proc_group2
        self.proc1.state = "done"
        self.proc2.state = "done"

        self.assertTrue(self.sale.shipped)

    def setUp(self):
        """Setup a Sale Order with 2 lines.
        And prepare procurements

        I use Model.new to get a model instance that is not saved to the
        database, but has working methods.

        """
        super(TestSaleIsDelivered, self).setUp()
        so = self.env["sale.order"]
        sol = self.env["sale.order.line"]
        product = self.env["product.product"]
        procurement = self.env["procurement.order"]
        procurement_group = self.env["procurement.group"]
        self.sale = so.new()
        self.sale_line1 = sol.new()
        self.sale_line2 = sol.new()
        self.sale_line1.order_id = self.sale
        self.sale_line2.order_id = self.sale

        self.sale.order_line = sol.browse([self.sale_line1.id, self.sale_line2.id])

        self.proc1 = procurement.new()
        self.proc_group1 = procurement_group.new()
        self.proc_group1.procurement_ids = self.proc1

        self.proc2 = procurement.new()
        self.proc_group2 = procurement_group.new()
        self.proc_group2.procurement_ids = self.proc2

        self.service_product = product.new({"type": "service"})
