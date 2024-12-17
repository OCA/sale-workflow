# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestProductTaskRecurrency(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.SaleTemplate = cls.env["sale.order.template"]
        cls.product_1 = cls.Product.create({"name": "Product 1"})
        cls.product_2 = cls.Product.create({"name": "Product 2"})
        cls.product_3 = cls.Product.create({"name": "Product 3"})
        cls.sale_template_1 = cls.SaleTemplate.create(
            {
                "name": "Template",
                "sale_order_template_line_ids": [
                    (0, 0, {"product_id": cls.product_1.id, "sequence": 20}),
                    (0, 0, {"product_id": cls.product_2.id, "sequence": 30}),
                ],
            }
        )
        cls.sale_template_2 = cls.SaleTemplate.create(
            {
                "name": "Template",
                "sale_order_template_line_ids": [
                    (0, 0, {"product_id": cls.product_3.id, "sequence": 40})
                ],
            }
        )

    def test_sale_order_template(self):
        with Form(self.env["sale.order"]) as sale_order_form:
            sale_order_form.partner_id = self.partner
            sale_order_form.sale_order_template_id = self.sale_template_1
            self.assertEqual(len(sale_order_form.order_line), 2)
            self.assertFalse(sale_order_form.sale_order_template_id)
            sale_order_form.sale_order_template_id = self.sale_template_2
            self.assertEqual(len(sale_order_form.order_line), 3)
            self.assertFalse(sale_order_form.sale_order_template_id)
        sale_order = sale_order_form.save()
        self.assertEqual(sale_order.order_line[0].sequence, 20)
        self.assertEqual(sale_order.order_line[0].product_id, self.product_1)
        self.assertEqual(sale_order.order_line[1].sequence, 40)
        self.assertEqual(sale_order.order_line[1].product_id, self.product_2)
        # the sequence is -99 because it is the first line in the second template
        # so, reset the sequence to 10 + max_sequence(40) = 50
        self.assertEqual(sale_order.order_line[2].sequence, 50)
        self.assertEqual(sale_order.order_line[2].product_id, self.product_3)
