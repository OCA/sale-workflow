# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestSale(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_9 = cls.env.ref("product.product_product_9")
        cls.product_11 = cls.env.ref("product.product_product_11")

        cls.sot = cls.env["sale.order.template"].create({"name": "Test QT"})

    def _create_wizard_items(self, so_template, products):
        """Create a wizard for `so_template` and select `products`."""
        wizard_form = common.Form(
            self.env["sale.template.add.products"].with_context(
                active_id=so_template.id,
                active_model=so_template._name,
            )
        )
        for product in products:
            wizard_form.product_ids.add(product)
        wizard = wizard_form.save()
        wizard.create_items()
        return wizard

    def test_import_product(self):
        """Create sale.order.template
        Import products
        Check products are presents
        """
        sot = self.sot
        wizard = self._create_wizard_items(sot, [self.product_9, self.product_11])
        wizard.item_ids[0].quantity = 4
        wizard.item_ids[1].quantity = 6
        wizard.select_products()
        self.assertEqual(len(sot.sale_order_template_line_ids), 2)
        for line in sot.sale_order_template_line_ids:
            if line.product_id.id == self.product_9.id:
                self.assertEqual(line.product_uom_qty, 4)
            else:
                self.assertEqual(line.product_uom_qty, 6)
