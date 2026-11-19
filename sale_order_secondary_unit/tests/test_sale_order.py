# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "list_price": 1000,
            }
        )
        # Set secondary uom on product template
        cls.product.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "unit-500",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        },
                    )
                ],
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product.product_tmpl_id.id)]
        )
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        with Form(cls.env["sale.order"]) as order_form:
            order_form.partner_id = cls.partner
            with order_form.order_line.new() as line_form:
                line_form.product_id = cls.product
                line_form.product_uom_qty = 1
        cls.order = order_form.save()

    def test_onchange_secondary_uom(self):
        self.order.order_line.write(
            {"secondary_uom_id": self.secondary_unit.id, "secondary_uom_qty": 5}
        )
        self.order.order_line._compute_product_uom_qty()
        self.assertEqual(self.order.order_line.product_uom_qty, 2.5)

    def test_onchange_secondary_unit_product_uom_qty(self):
        self.order.order_line.update(
            {"secondary_uom_id": self.secondary_unit.id, "product_uom_qty": 3.5}
        )
        self.assertEqual(self.order.order_line.secondary_uom_qty, 7.0)

    def test_default_secondary_unit(self):
        self.order.order_line._onchange_product_id_secondary_uom()
        self.assertEqual(self.order.order_line.secondary_uom_id, self.secondary_unit)

    def test_onchange_order_product_uom(self):
        self.order.order_line.update(
            {
                "secondary_uom_id": self.secondary_unit.id,
                "product_uom_id": self.product_uom_gram.id,
                "product_uom_qty": 3500.00,
            }
        )
        self.assertEqual(self.order.order_line.secondary_uom_qty, 7.0)

    def test_independent_type(self):
        # dependent type is already tested as dependency_type by default
        self.order.order_line.secondary_uom_id = self.secondary_unit.id
        self.order.order_line.secondary_uom_id.write({"dependency_type": "independent"})

        # Remember previous UoM quantity for avoiding interactions with other modules
        # Force product_uom_qty too to avoid that product_secondary_unit
        # _compute_helper_target_field_qty break process when product_uom_qty == 0
        previous_uom_qty = self.order.order_line.product_uom_qty = 9
        self.order.order_line.write({"secondary_uom_qty": 2})
        self.assertEqual(self.order.order_line.product_uom_qty, previous_uom_qty)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 2)

        self.order.order_line.write({"product_uom_qty": 17})
        self.assertEqual(self.order.order_line.secondary_uom_qty, 2)
        self.assertEqual(self.order.order_line.product_uom_qty, 17)

    def test_secondary_uom_unit_price(self):
        # Remove secondary uom in sale line to do a complete test of secondary price
        self.order.order_line.secondary_uom_id = False
        self.assertEqual(self.order.order_line.secondary_uom_unit_price, 0)
        self.order.order_line.update(
            {"secondary_uom_id": self.secondary_unit.id, "product_uom_qty": 2}
        )

        self.assertEqual(self.order.order_line.secondary_uom_qty, 4)
        self.assertEqual(self.order.order_line.secondary_uom_unit_price, 500)

        self.order.order_line.write({"product_uom_qty": 8})
        self.assertEqual(self.order.order_line.secondary_uom_qty, 16)
        self.assertEqual(self.order.order_line.secondary_uom_unit_price, 500)
        self.assertEqual(self.order.order_line.price_subtotal, 8000)


@tagged("post_install", "-at_install")
class TestSaleOrderLineDefaultQty(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids += cls.env.ref("uom.group_uom")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")

    def _product_with_secondary_unit(self, factor, dependency_type="dependent"):
        product = self.env["product.product"].create(
            {
                "name": f"test - secondary {factor} {dependency_type}",
                "list_price": 100.0,
            }
        )
        product.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": f"box-{factor}",
                            "uom_id": self.product_uom_unit.id,
                            "factor": factor,
                            "dependency_type": dependency_type,
                        },
                    )
                ],
            }
        )
        product.sale_secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0].id
        return product

    def _line_from_form(self, product, qty_before_product=None):
        with Form(self.env["sale.order"]) as order_form:
            order_form.partner_id = self.partner
            with order_form.order_line.new() as line_form:
                if qty_before_product is not None:
                    line_form.product_uom_qty = qty_before_product
                line_form.product_id = product
        return order_form.save().order_line

    def test_qty_on_product_set_keeps_default_one(self):
        for factor in (1.0, 12.0):
            with self.subTest(factor=factor):
                product = self._product_with_secondary_unit(factor)
                line = self._line_from_form(product)
                self.assertEqual(line.secondary_uom_id, product.sale_secondary_uom_id)
                self.assertEqual(line.product_uom_qty, 1.0)

    def test_qty_typed_before_product_is_kept(self):
        for factor in (1.0, 12.0):
            with self.subTest(factor=factor):
                product = self._product_with_secondary_unit(factor)
                line = self._line_from_form(product, qty_before_product=5.0)
                self.assertEqual(line.secondary_uom_id, product.sale_secondary_uom_id)
                self.assertEqual(line.product_uom_qty, 5.0)

    def test_qty_on_product_without_secondary_unit(self):
        product = self.env["product.product"].create(
            {"name": "test - no secondary", "list_price": 100.0}
        )
        self.assertEqual(self._line_from_form(product).product_uom_qty, 1.0)
        self.assertEqual(
            self._line_from_form(product, qty_before_product=5.0).product_uom_qty, 5.0
        )

    def test_independent_secondary_qty_on_product_set(self):
        for factor in (1.0, 12.0):
            with self.subTest(factor=factor):
                product = self._product_with_secondary_unit(
                    factor, dependency_type="independent"
                )
                line = self._line_from_form(product)
                self.assertEqual(line.product_uom_qty, 1.0)
                self.assertEqual(line.secondary_uom_qty, 1.0)

    def test_independent_secondary_qty_with_typed_qty(self):
        product = self._product_with_secondary_unit(12.0, dependency_type="independent")
        line = self._line_from_form(product, qty_before_product=5.0)
        self.assertEqual(line.product_uom_qty, 5.0)
        self.assertEqual(line.secondary_uom_qty, 0.0)
