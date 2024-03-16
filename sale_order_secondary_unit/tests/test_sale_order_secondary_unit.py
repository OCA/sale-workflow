# Copyright 2018-2020 Tecnativa - Carlos Dauden
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests import Form, TransactionCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestSaleOrderSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "list_price": 1000.00,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
            }
        )
        cls.product.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "unit-500",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        }
                    )
                ],
            }
        )
        cls.price_list = cls.env["product.pricelist"].create(
            {
                "name": "price list for test",
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product.product_tmpl_id.id)]
        )
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        with Form(cls.env["sale.order"]) as order_form:
            order_form.partner_id = cls.partner
            order_form.pricelist_id = cls.price_list
            with order_form.order_line.new() as line_form:
                line_form.product_id = cls.product
                line_form.product_uom_qty = 1
        cls.order = order_form.save()

    def test_compute_product_uom_qty(self):
        self.order.order_line.write(
            {"secondary_uom_id": self.secondary_unit.id, "secondary_uom_qty": 5}
        )
        self.assertEqual(self.order.order_line.product_uom_qty, 2.5)

    def test_compute_secondary_uom_qty(self):
        self.order.order_line.write(
            {"secondary_uom_id": self.secondary_unit.id, "product_uom_qty": 3.5}
        )
        self.assertEqual(self.order.order_line.secondary_uom_qty, 7.0)

        self.order.order_line.write(
            {
                "secondary_uom_id": self.secondary_unit.id,
                "product_uom": self.product_uom_gram.id,
                "product_uom_qty": 3500.00,
            }
        )
        self.assertEqual(self.order.order_line.secondary_uom_qty, 7.0)

    def test_default_secondary_unit(self):
        self.order.order_line._onchange_product_id()
        self.assertEqual(self.order.order_line.secondary_uom_id, self.secondary_unit)

    def test_independent_type(self):
        # dependent type is already tested as dependency_type by default
        self.order.order_line.secondary_uom_id = self.secondary_unit.id
        self.order.order_line.secondary_uom_id.write({"dependency_type": "independent"})

        # Remember previous UoM quantity for avoiding interactions with other modules
        previous_uom_qty = self.order.order_line.product_uom_qty
        self.order.order_line.write({"secondary_uom_qty": 2})
        self.assertEqual(self.order.order_line.product_uom_qty, previous_uom_qty)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 2)

        self.order.order_line.write({"product_uom_qty": 17})
        self.assertEqual(self.order.order_line.secondary_uom_qty, 2)
        self.assertEqual(self.order.order_line.product_uom_qty, 17)

    def test_secondary_uom_price_unit(self):
        self.order.order_line.secondary_uom_id = False
        self.assertEqual(self.order.order_line.product_uom_qty, 1)
        self.assertEqual(self.order.order_line.price_unit, 1000)
        self.assertEqual(self.order.order_line.price_subtotal, 1000)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 0)
        self.assertEqual(self.order.order_line.secondary_uom_price_unit, 0)

        self.order.order_line.write(
            {"secondary_uom_id": self.secondary_unit.id, "product_uom_qty": 2}
        )
        self.assertEqual(self.order.order_line.product_uom_qty, 2)
        self.assertEqual(self.order.order_line.price_unit, 1000)
        self.assertEqual(self.order.order_line.price_subtotal, 2000)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 4)
        self.assertEqual(self.order.order_line.secondary_uom_price_unit, 500)

        self.order.order_line.write({"product_uom_qty": 8})
        self.assertEqual(self.order.order_line.price_subtotal, 8000)
        self.assertEqual(self.order.order_line.secondary_uom_qty, 16)
        self.assertEqual(self.order.order_line.secondary_uom_price_unit, 500)
