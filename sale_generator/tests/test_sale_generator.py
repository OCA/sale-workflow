# 2017 EBII Monsieurb <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleGenerator(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner1 = self.env.ref("base.res_partner_address_4")
        self.partner2 = self.env.ref("base.res_partner_address_27")
        self.demo_sale_order = self.env.ref("sale.sale_order_4")
        self.some_fields_to_compare_so = [
            "validity_date",
            "payment_term_id",
            "state",
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

    def test_basic_generation(self):
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
        sg = self.env["sale.generator"].create(vals)

        sg.button_generate_sale_orders()

        sales_generated = self.env["sale.order"].search(
            [("generator_id", "=", sg.id)]
        )
        self.assertEqual(len(sales_generated), 2)
        for sale in sales_generated:
            self.assertEqual(sale.state, "draft")

        sg.action_confirm()

        for sale in sales_generated:
            for field in self.some_fields_to_compare_so:
                self.assertEqual(
                    getattr(self.demo_sale_order, field), getattr(sale, field)
                )
            for field, val in self.constant_values_for_generated_sos.items():
                self.assertEqual(getattr(sale, field), val)
            self._helper_test_order_line_equality(self.demo_sale_order, sale)
