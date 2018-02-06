# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import odoo.tests.common as common


class TestSaleLastPriceInfo(common.TransactionCase):

    def setUp(self):
        super(TestSaleLastPriceInfo, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']
        self.sale_order = self.env.ref('sale.sale_order_4')
        self.sale_line = self.env.ref('sale.sale_order_line_9')
        self.partner = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_delivery_02')
        self.price_unit = 100.0

    def test_sale_last_price_info_demo(self):
        sale_lines = self.sale_line_model.search(
            [('product_id', '=', self.product.id),
             ('state', 'in', ['sale', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.assertEqual(
            datetime.strptime(
                sale_lines[:1].order_id.date_order,
                "%Y-%m-%d %H:%M:%S").date(),
            datetime.strptime(self.product.last_sale_date, "%Y-%m-%d").date())
        self.assertEqual(
            sale_lines[:1].price_unit, self.product.last_sale_price)
        self.assertEqual(
            sale_lines[:1].order_id.partner_id, self.product.last_customer_id)
