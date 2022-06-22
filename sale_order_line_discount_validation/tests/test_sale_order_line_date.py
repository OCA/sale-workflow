import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrderLineDiscountValidatons(TransactionCase):
    def setUp(self):
        """Setup a Sale Order with 4 lines."""
        super(TestSaleOrderLineDiscountValidatons, self).setUp()
        customer = self.env.ref("base.res_partner_3")
        self.company = self.env.ref("base.main_company")
        self.company.security_lead = 1

        price = 100.0
        qty = 5
        product_id = self.env.ref("product.product_product_7")
        self.today = fields.Datetime.now()
        self.dt1 = self.today + datetime.timedelta(days=9)
        self.dt2 = self.today + datetime.timedelta(days=10)
        self.dt3 = self.today + datetime.timedelta(days=3)
        self.sale1 = self._create_sale_order(customer, self.dt2)
        self.sale_line1 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, self.dt1
        )
        self.sale_line2 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, self.dt2
        )
        self.sale_line3 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, None
        )
        self.sale2 = self._create_sale_order(customer, self.dt2)
        self.sale_line4 = self._create_sale_order_line(
            self.sale2, product_id, qty, price, self.dt3
        )
        self.sale_line5 = self._create_sale_order_line(
            self.sale2, product_id, qty, price, self.dt2
        )
        self.sale_line6 = self._create_sale_order_line(
            self.sale2, product_id, qty, price, self.dt1
        )

    def _create_sale_order(self, customer, date):
        sale = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "partner_invoice_id": customer.id,
                "partner_shipping_id": customer.id,
                "commitment_date": date,
                "picking_policy": "direct",
            }
        )
        return sale

    def _create_sale_order_line(self, sale, product, qty, price, date):
        sale_line = self.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "name": "cool product",
                "order_id": sale.id,
                "price_unit": price,
                "product_uom_qty": qty,
                "commitment_date": date,
            }
        )
        return sale_line

    def _assert_equal_dates(self, date1, date2):
        if isinstance(date1, datetime.datetime):
            date1 = date1.date()
        if isinstance(date2, datetime.datetime):
            date2 = date2.date()
        self.assertEqual(date1, date2)

    def test01_get_message_body_everything_none(self):
        body = self.sale1._get_message_body()
        self.assertEqual(body, "")

    def test02_get_message_body_confirm(self):
        body = self.sale1._get_message_body(is_confirm=True)
        assert "is ready for your approval" in body

    def test03_get_message_body_refuse(self):
        body = self.sale1._get_message_body(is_refuse=True)
        assert "Hello," in body
        assert "Quotation" in body
        assert "is refused." in body

    def test04_get_message_body_approve(self):
        body = self.sale1._get_message_body(is_approve=True)
        assert "Hello," in body
        assert "Quotation" in body
        assert "is approved." in body

    def test05_request_approval(self):
        approval = self.sale1._request_approval()
        self.assertEqual(approval, 13)
