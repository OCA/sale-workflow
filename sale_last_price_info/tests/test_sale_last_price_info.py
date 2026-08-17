# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestSaleLastPriceInfo(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_line_model = cls.env["sale.order.line"]
        cls.sale_order = cls.env.ref("sale.sale_order_4")
        cls.sale_line = cls.env.ref("sale.sale_order_line_9")
        cls.partner = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_delivery_02")
        cls.price_unit = 100.0

    def test_sale_last_price_info_demo(self):
        sale_line = self.sale_line_model.search(
            [("product_id", "=", self.product.id), ("state", "=", "sale")],
            limit=1,
            order="date_order_sale_last_price_info desc",
        )
        self.assertEqual(
            sale_line.date_order_sale_last_price_info.date(),
            self.product.last_sale_date,
        )
        self.assertEqual(sale_line.price_unit, self.product.last_sale_price)
        self.assertEqual(sale_line.order_id.partner_id, self.product.last_customer_id)
