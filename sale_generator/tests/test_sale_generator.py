# 2017 EBII Monsieurb <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-post_install", "at_install")
class TestSaleGenerator(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner1 = self.env.ref("base.res_partner_address_4")
        self.partner2 = self.env.ref("base.res_partner_address_27")
        self.partner3 = self.env.ref("base.res_partner_10")
        self.demo_sale_order = self.env.ref("sale.sale_order_4")
        self.some_fields_to_compare_so = [
            "validity_date",
            "payment_term_id",
        ]
        self.some_fields_to_compare_so_line = [
            "product_id",
            "name",
            "product_uom_qty",
            "price_unit",
            "tax_id",
        ]
        self.constant_values_for_generated_sos = {
            "active": True,
            "is_template": False,
        }

    def _helper_test_order_line_equality(self, so1, so2):
        self.assertEqual(len(so1.order_line.ids), len(so2.order_line.ids))
        len_lines = len(so1.order_line.ids)
        for itr in range(len_lines):
            for field in self.some_fields_to_compare_so_line:
                line1 = so1.order_line[itr]
                line2 = so2.order_line[itr]
                self.assertEqual(getattr(line1, field), getattr(line2, field))

    def _helper_test_so_equality(self, base_SO, sale_orders):
        for sale in sale_orders:
            for field in self.some_fields_to_compare_so:
                self.assertEqual(getattr(base_SO, field), getattr(sale, field))
            for field, val in self.constant_values_for_generated_sos.items():
                self.assertEqual(getattr(sale, field), val)
            self._helper_test_order_line_equality(base_SO, sale)

    def test_generation_workflow(self):
        sale_tmpl = self.demo_sale_order
        part1 = self.partner1
        part2 = self.partner2
        vals = {
            "name": "/",
            "partner_ids": [(4, part1.id, 0), (4, part2.id, 0)],
            "tmpl_sale_id": sale_tmpl.id,
            "warehouse_id": self.env.ref("stock.stock_warehouse_shop0").id,
            "state": "draft",
            "company_id": self.ref("base.main_company"),
        }
        sale_generator = self.env["sale.generator"].create(vals)

        # Initial generation of sale order on confirmation
        sale_generator.button_generate_sale_orders()
        sales_generated = self.env["sale.order"].search(
            [("generator_id", "=", sale_generator.id)]
        )
        self.assertEqual(len(sales_generated), 2)
        for sale in sales_generated:
            self.assertEqual(sale.state, "draft")
        self._helper_test_so_equality(self.demo_sale_order, sales_generated)

        # Dynamic update of generated sale orders
        sale_generator.partner_ids += self.partner3
        sales_generated = self.env["sale.order"].search(
            [("generator_id", "=", sale_generator.id)]
        )
        self.assertEqual(len(sales_generated), 3)
        for sale in sales_generated:
            self.assertEqual(sale.state, "draft")
        self._helper_test_so_equality(self.demo_sale_order, sales_generated)

        sale_generator.action_confirm()
        self._helper_test_so_equality(self.demo_sale_order, sales_generated)

    def test_create_partner_from_generator(self):
        sale_tmpl = self.demo_sale_order
        part1 = self.partner1
        part2 = self.partner2
        vals = {
            "name": "/",
            "partner_ids": [(4, part1.id, 0), (4, part2.id, 0)],
            "tmpl_sale_id": sale_tmpl.id,
            "warehouse_id": self.env.ref("stock.stock_warehouse_shop0").id,
            "state": "draft",
            "company_id": self.ref("base.main_company"),
        }
        sale_generator = self.env["sale.generator"].create(vals)

        # test special generator context: partner create
        test_partner = (
            self.env["res.partner"]
            .with_context({"from_generator_id": sale_generator.id})
            .create({"name": "test partner"})
        )
        self.assertEqual(
            sorted(sale_generator.partner_ids.ids),
            sorted((part1 + part2 + test_partner).ids),
        )
        # test special generator context: action
        close_action = (
            self.env["res.partner"]
            .with_context({"from_generator_id": sale_generator.id})
            .close_from_customer_wizard()
        )
        self.assertEqual(sale_generator.id, close_action["res_id"])
