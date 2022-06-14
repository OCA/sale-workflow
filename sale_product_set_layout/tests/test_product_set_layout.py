from odoo.tests import common


class TestProductSetLayout(common.TransactionCase):
    """Test Product set"""

    def setUp(self):
        super(TestProductSetLayout, self).setUp()
        self.product_set_add = self.env["product.set.add"]

    def test_add_set(self):
        so = self.env.ref("sale.sale_order_6")
        count_lines = len(so.order_line)
        product_set_without_section = self.env.ref(
            "sale_product_set.product_set_i5_computer"
        )
        product_set_with_section = self.env.ref("sale_product_set.product_set_services")
        so_set = self.product_set_add.with_context(active_id=so.id).create(
            {"product_set_id": product_set_without_section.id, "quantity": 2}
        )
        so_set.add_set()
        so_set = self.product_set_add.with_context(active_id=so.id).create(
            {"product_set_id": product_set_with_section.id, "quantity": 2}
        )
        so_set.add_set()
        # checking our sale order
        self.assertEqual(len(so.order_line), count_lines + 5)
        for line in so.order_line:
            for set_line in product_set_with_section.set_line_ids:
                if line.product_id.id == set_line.product_id.id:
                    self.assertEqual(
                        line.layout_category_id.id,
                        self.env.ref("sale.sale_layout_cat_1").id,
                    )
            for set_line in product_set_without_section.set_line_ids:
                if line.product_id.id == set_line.product_id.id:
                    self.assertFalse(line.layout_category_id.id)
