# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestSaleStockQuantityUpdatable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product test", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner test"})
        so_form = Form(cls.env["sale.order"])
        so_form.partner_id = cls.partner
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = cls.product
            soline_form.product_uom_qty = 2
        cls.sale_order = so_form.save()
        cls.packaging = cls.env["product.packaging"].create(
            [
                {
                    "name": "I'm a packaging",
                    "product_id": cls.product.id,
                    "qty": 1.0,
                },
            ]
        )

    def _check_fields_readonly(self, form, fields):
        """Assert that fields are readonly in the form."""
        with self.assertRaises(AssertionError):
            for field in fields:
                form.__setattr__(field, 1)

    def test_compute_quantity_updatable(self):
        test_cases = [
            (("draft", "manual"), True),
            (("sale", "manual"), True),
            (("sale", "stock_move"), False),
            (("done", None), False),
        ]
        test_order_line = self.sale_order.order_line[0]
        test_order_line.product_packaging_id = self.packaging
        test_order_line.product_packaging_qty = 1.0

        for (state, qty_delivered_method), expected_quantiy_updatable in test_cases:
            test_order_line.write({"qty_delivered_method": qty_delivered_method})
            self.sale_order.write({"state": state})
            self.assertEqual(
                test_order_line.quantity_updatable, expected_quantiy_updatable
            )

            if not test_order_line.quantity_updatable:
                form = Form(self.sale_order)
                self._check_fields_readonly(
                    form,
                    [
                        "product_uom_qty",
                        "product_packaging_id",
                        "product_packaging_qty",
                    ],
                )
