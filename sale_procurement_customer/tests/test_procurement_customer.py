# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestProcurementCustomer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_obj = cls.env["res.partner"]
        cls.sale_obj = cls.env["sale.order"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
            }
        )
        cls.customer = cls.partner_obj.create(
            {
                "name": "Customer 1",
            }
        )
        cls.customer_2 = cls.partner_obj.create(
            {
                "name": "Customer 2",
            }
        )
        cls.env.user.groups_id += cls.env.ref("account.group_delivery_invoice_address")

    def test_sale(self):
        """
        - Create a sale order with Customer 2 as invoiced partner
        - Set the Customer 1 as shipping partner
        - Procurement should contain Customer 2 as customer (customer_id)
        """
        with Form(self.sale_obj) as sale_form:
            sale_form.partner_id = self.customer_2
            sale_form.partner_shipping_id = self.customer
            with (sale_form.order_line.new()) as line_form:
                line_form.product_id = self.product
        sale = sale_form.save()

        sale.action_confirm()
        self.assertEqual(sale.procurement_group_id.customer_id, self.customer_2)
        self.assertEqual(sale.procurement_group_id.partner_id, self.customer)
