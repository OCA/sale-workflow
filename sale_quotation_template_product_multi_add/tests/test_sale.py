import odoo.tests.common as common


class TestSale(common.TransactionCase):
    def setUp(self):
        super(TestSale, self).setUp()
        self.product_9 = self.env.ref("product.product_product_9")
        self.product_11 = self.env.ref("product.product_product_11")

    def test_import_product(self):
        """Create sale.order.template
        Import products
        Check products are presents
        """
        sot = self.env["sale.order.template"].create({"name": "Test QT"})
        wiz_obj = self.env["sale.template.add.products"]
        wizard = wiz_obj.with_context(
            active_id=sot.id, active_model="sale.order.template"
        )
        products = [(6, 0, [self.product_9.id, self.product_11.id])]
        wizard_id = wizard.create({"product_ids": products})
        wizard_id.create_items()
        wizard_id.item_ids[0].quantity = 4
        wizard_id.item_ids[1].quantity = 6
        wizard_id.select_products()
        self.assertEqual(len(sot.sale_order_template_line_ids), 2)
        for line in sot.sale_order_template_line_ids:
            if line.product_id.id == self.product_9.id:
                self.assertEqual(line.product_uom_qty, 4)
            else:
                self.assertEqual(line.product_uom_qty, 6)
