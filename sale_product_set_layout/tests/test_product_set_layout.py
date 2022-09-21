from odoo.tests import common


class TestProductSetLayout(common.TransactionCase):
    """Test Product set"""

    def setUp(self):
        super(TestProductSetLayout, self).setUp()
        self.product_set_add = self.env["product.set.add"]

    def test_add_set(self):
        so = self.env.ref("sale.sale_order_6")
        base_line_ids = so.order_line
        count_lines = len(so.order_line)
        product_set_with_section = self.env.ref("sale_product_set.product_set_services")
        so_set = self.product_set_add.create(
            {
                "product_set_id": product_set_with_section.id,
                "quantity": 2,
                "order_id": so.id,
            }
        )
        so_set.add_set()
        self.assertEqual(len(so.order_line), count_lines + 3)
        products_in_set = product_set_with_section.set_line_ids.filtered(
            lambda a: a.product_id
        ).mapped("product_id")
        # Check lines with products
        for line in so.order_line.filtered(
            lambda a: a.id not in base_line_ids.ids and a.product_id
        ):
            self.assertFalse(line.display_type)
            self.assertTrue(line.product_id.id in products_in_set.ids)
        # Test sections
        for line in so.order_line.filtered(
            lambda a: a.id not in base_line_ids.ids and not a.product_id
        ):
            self.assertEqual(
                line.display_type,
                "line_section",
            )
