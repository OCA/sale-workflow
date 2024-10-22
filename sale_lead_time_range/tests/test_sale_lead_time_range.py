# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from freezegun import freeze_time

from odoo.tests import Form, TransactionCase


class TestSaleLeadTimeRange(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.so_model = cls.env["sale.order"]
        cls.sol_model = cls.env["sale.order.line"]
        cls.product_model = cls.env["product.product"]

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_9")

        product_form = Form(cls.product_model)
        product_form.name = "Test Product"
        product_form.sale_delay = 6
        product_form.sale_delay_range_value = 6
        product_form.sale_delay_range_type = "days"
        cls.product = product_form.save()

        cls.sale_order = cls.so_model.create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.sale_order_line = cls.sol_model.create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
            }
        )

    @freeze_time("2024-04-11")
    def test_product_template_sale_delay_time_range(self):
        self.product.sale_delay_range_value = 3
        self.assertEqual(self.product.sale_delay, 3)
        self.product.sale_delay_range_value = 2
        self.product.sale_delay_range_type = "weeks"
        self.assertEqual(self.product.sale_delay, 14)
        self.product.sale_delay_range_value = 4
        self.product.sale_delay_range_type = "months"
        self.assertEqual(self.product.sale_delay, 122)
        self.product.sale_delay_range_value = 1
        self.product.sale_delay_range_type = "years"
        self.assertEqual(self.product.sale_delay, 365)

    @freeze_time("2024-04-11")
    def test_sale_order_line_customer_lead_time_range(self):
        self.sale_order_line.customer_lead_range_value = 2
        self.sale_order_line.customer_lead_range_type = "weeks"
        self.assertEqual(self.sale_order_line.customer_lead, 14)
        self.sale_order_line.customer_lead_range_value = 2
        self.sale_order_line.customer_lead_range_type = "months"
        self.assertEqual(self.sale_order_line.customer_lead, 61)
        self.sale_order_line.customer_lead_range_value = 2
        self.sale_order_line.customer_lead_range_type = "years"
        self.assertEqual(self.sale_order_line.customer_lead, 730)
