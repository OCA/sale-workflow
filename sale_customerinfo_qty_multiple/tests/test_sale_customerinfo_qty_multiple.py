# Copyright 2026 Aures Tic Consultors S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestSaleCustomerinfoQtyMultiple(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.dozen = cls.env.ref("uom.product_uom_dozen")
        cls.customer = cls.env["res.partner"].create({"name": "Distributor"})
        cls.contact = cls.env["res.partner"].create(
            {"name": "Buyer", "parent_id": cls.customer.id}
        )
        cls.other = cls.env["res.partner"].create({"name": "Other customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Gloves", "uom_id": cls.unit.id, "uom_po_id": cls.unit.id}
        )
        cls.customerinfo = cls.env["product.customerinfo"].create(
            {
                "partner_id": cls.customer.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_code": "D-GLOVES",
                "sale_qty_multiple": 50,
                "sale_qty_multiple_policy": "down",
            }
        )

    def _order_form(self, partner=None):
        form = Form(self.env["sale.order"])
        form.partner_id = partner or self.customer
        return form

    def _line(self, qty, partner=None):
        order = self.env["sale.order"].create(
            {
                "partner_id": (partner or self.customer).id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": qty})
                ],
            }
        )
        return order.order_line

    def test_form_product_starts_at_multiple(self):
        form = self._order_form()
        with form.order_line.new() as line:
            line.product_id = self.product
            self.assertEqual(line.product_uom_qty, 50)

    @mute_logger("odoo.tests.form.onchange")
    def test_form_round_down(self):
        form = self._order_form()
        with form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 63
            self.assertEqual(line.product_uom_qty, 50)
            self.assertEqual(line.customer_qty_multiple, 50)
        order = form.save()
        self.assertEqual(order.order_line.product_uom_qty, 50)

    @mute_logger("odoo.tests.form.onchange")
    def test_form_round_up(self):
        self.customerinfo.sale_qty_multiple_policy = "up"
        form = self._order_form()
        with form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 63
            self.assertEqual(line.product_uom_qty, 100)

    @mute_logger("odoo.tests.form.onchange")
    def test_form_round_nearest(self):
        self.customerinfo.sale_qty_multiple_policy = "nearest"
        form = self._order_form()
        with form.order_line.new() as line:
            line.product_id = self.product
            for ordered, expected in (
                (80, 100),
                (75, 100),
                (74, 50),
                (124, 100),
                (20, 50),
                (1, 50),
            ):
                line.product_uom_qty = ordered
                self.assertEqual(line.product_uom_qty, expected, ordered)

    def test_created_by_code_nearest(self):
        self.customerinfo.sale_qty_multiple_policy = "nearest"
        self.assertEqual(self._line(75).product_uom_qty, 100)
        self.assertEqual(self._line(74).product_uom_qty, 50)
        self.assertEqual(self._line(20).product_uom_qty, 50)

    @mute_logger("odoo.tests.form.onchange")
    def test_form_only_warning(self):
        self.customerinfo.sale_qty_multiple_policy = "warning"
        form = self._order_form()
        with form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 63
            self.assertEqual(line.product_uom_qty, 63)
            self.assertTrue(line.is_not_customer_qty_multiple)
            line.product_uom_qty = 150
            self.assertFalse(line.is_not_customer_qty_multiple)

    def test_created_by_code(self):
        line = self._line(130)
        self.assertEqual(line.product_uom_qty, 100)
        self.assertIn("130", line.order_id.message_ids[0].body)
        line.product_uom_qty = 220
        self.assertEqual(line.product_uom_qty, 200)
        line.with_context(skip_customer_qty_multiple=True).product_uom_qty = 75
        self.assertEqual(line.product_uom_qty, 75)

    def test_multiple_already(self):
        line = self._line(150)
        self.assertEqual(line.product_uom_qty, 150)
        self.assertFalse(line.is_not_customer_qty_multiple)

    def test_contact_of_the_customer(self):
        """The customer info of the company applies to its contacts."""
        line = self._line(63, partner=self.contact)
        self.assertEqual(line.product_uom_qty, 50)

    def test_other_customer(self):
        line = self._line(63, partner=self.other)
        self.assertEqual(line.product_uom_qty, 63)
        self.assertFalse(line.customer_qty_multiple)

    def test_line_in_other_unit(self):
        """A multiple of 24 units, ordered in dozens: 5 dozens = 60 units,
        rounded down to 48 units = 4 dozens."""
        self.customerinfo.sale_qty_multiple = 24
        order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.dozen.id,
                            "product_uom_qty": 5,
                        },
                    )
                ],
            }
        )
        self.assertEqual(order.order_line.product_uom_qty, 4)

    def test_confirmed_order_untouched(self):
        line = self._line(100)
        line.order_id.action_confirm()
        line.product_uom_qty = 130
        self.assertEqual(line.product_uom_qty, 130)
