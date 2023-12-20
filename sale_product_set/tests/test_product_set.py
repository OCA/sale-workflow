# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions
from odoo.tests import common


class TestProductSet(common.TransactionCase):
    """Test Product set"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.so_model = cls.env["sale.order"]
        cls.so = cls.env.ref("sale.sale_order_6")
        cls.product_set_add = cls.env["product.set.add"]
        cls.product_set = cls.env.ref("product_set.product_set_i5_computer")

    def _get_wiz(self, ctx=None, **kw):
        vals = {
            "product_set_id": self.product_set.id,
            "order_id": self.so.id,
            "quantity": 2,
        }
        vals.update(kw)
        return self.product_set_add.with_context(**ctx or {}).create(vals)

    def test_add_set_lines_init(self):
        wiz = self._get_wiz()
        # Default to all lines from set
        self.assertEqual(wiz.product_set_line_ids, self.product_set.set_line_ids)
        self.assertEqual(
            [x.id for x in wiz._get_lines()], self.product_set.set_line_ids.ids
        )
        # Pass via ctx
        line_ids = self.env.ref("product_set.product_set_line_computer_1").ids
        wiz = self._get_wiz(ctx=dict(product_set_add__set_line_ids=line_ids))
        self.assertEqual(wiz.product_set_line_ids.ids, line_ids)
        self.assertEqual([x.id for x in wiz._get_lines()], line_ids)
        # Pass at create
        line_ids = self.env.ref("product_set.product_set_line_computer_3").ids
        wiz = self._get_wiz()
        wiz.product_set_line_ids = line_ids
        self.assertEqual(wiz.product_set_line_ids.ids, line_ids)
        self.assertEqual([x.id for x in wiz._get_lines()], line_ids)

    def test_add_set(self):
        so = self.so
        count_lines = len(so.order_line)
        # Simulation the opening of the wizard and adding a set on the
        # current sale order
        wiz = self._get_wiz()
        wiz.add_set()
        # checking our sale order
        self.assertEqual(len(so.order_line), count_lines + 3)
        # check all lines are included
        for line in self.product_set.set_line_ids:
            order_line = so.order_line.filtered(
                lambda x: x.product_id == line.product_id
            )
            order_line.ensure_one()
            self.assertEqual(order_line.product_uom_qty, line.quantity * wiz.quantity)

        sequence = {}
        for line in so.order_line:
            sequence[line.product_id.id] = line.sequence
        # make sure sale order line sequence keep sequence set on set
        seq_line1 = sequence.pop(
            self.env.ref("product_set.product_set_line_computer_4").product_id.id
        )
        seq_line2 = sequence.pop(
            self.env.ref("product_set.product_set_line_computer_1").product_id.id
        )
        seq_line3 = sequence.pop(
            self.env.ref("product_set.product_set_line_computer_3").product_id.id
        )
        self.assertTrue(
            max(v for k, v in sequence.items()) < seq_line1 < seq_line2 < seq_line3
        )

    def test_add_set_sequence(self):
        so = self.so
        count_lines = len(so.order_line)
        # Start from -1 to have mixed negative, null and positive (-1, 0, 1)
        for seq, line in enumerate(self.product_set.set_line_ids, start=-1):
            line.write({"sequence": seq})
        wiz = self._get_wiz()
        wiz.add_set()
        sequence = {line.product_id: line.sequence for line in so.order_line}
        self.assertEqual(len(so.order_line), count_lines + 3)
        # make sure sale order line sequence keep sequence set on set
        seq_line1 = sequence.pop(
            self.env.ref("product_set.product_set_line_computer_4").product_id
        )
        seq_line2 = sequence.pop(
            self.env.ref("product_set.product_set_line_computer_1").product_id
        )
        seq_line3 = sequence.pop(
            self.env.ref("product_set.product_set_line_computer_3").product_id
        )
        self.assertTrue(
            max(v for k, v in sequence.items()) < seq_line1 < seq_line2 < seq_line3
        )

    def test_delete_set(self):
        # Simulation the opening of the wizard and adding a set on the
        # current sale order
        wiz = self._get_wiz()
        self.product_set.unlink()
        self.assertFalse(wiz.exists())

    def test_add_set_on_empty_so(self):
        so = self.so_model.create({"partner_id": self.ref("base.res_partner_1")})
        wiz = self._get_wiz(order_id=so.id)
        wiz.add_set()
        self.assertEqual(len(so.order_line), 3)

    def test_add_set_non_matching_partner(self):
        so = self.so_model.create({"partner_id": self.ref("base.res_partner_1")})
        self.product_set.partner_id = self.ref("base.res_partner_2")
        wiz = self._get_wiz(order_id=so.id)
        with self.assertRaises(exceptions.ValidationError):
            wiz.add_set()

    def test_add_set_non_matching_partner_ctx_bypass(self):
        so = self.so_model.create({"partner_id": self.ref("base.res_partner_1")})
        self.assertEqual(len(so.order_line), 0)
        self.product_set.partner_id = self.ref("base.res_partner_2")
        wiz = self._get_wiz(order_id=so.id).with_context(
            product_set_add_skip_validation=True
        )
        wiz.add_set()
        self.assertEqual(len(so.order_line), 3)

    def test_add_set_non_matching_partner_ctx_override(self):
        so = self.so_model.create({"partner_id": self.ref("base.res_partner_1")})
        self.assertEqual(len(so.order_line), 0)
        wiz = self._get_wiz(order_id=so.id).with_context(
            allowed_order_partner_ids=[self.ref("base.res_partner_2")]
        )
        wiz.add_set()
        self.assertEqual(len(so.order_line), 3)

    def test_add_set_no_update_existing_products(self):
        so = self.so_model.create({"partner_id": self.ref("base.res_partner_1")})
        wiz = self._get_wiz(order_id=so.id)
        wiz.add_set()
        self.assertEqual(len(so.order_line), 3)
        # if we run it again by default the wizard sums up quantities
        wiz.add_set()
        self.assertEqual(len(so.order_line), 6)
        # but we can turn it off
        wiz.skip_existing_products = True
        wiz.add_set()
        self.assertEqual(len(so.order_line), 6)

    def test_discount(self):
        product_test = self.env["product.product"].create(
            {"name": "Test", "list_price": 100.0}
        )
        set_line = self.env["product.set.line"].create(
            {"product_id": product_test.id, "quantity": 1, "discount": 50}
        )
        prod_set = self.env["product.set"].create(
            {"name": "Test", "set_line_ids": [(4, set_line.id)]}
        )
        so = self.env.ref("sale.sale_order_6")
        wiz = self.product_set_add.create(
            {"order_id": so.id, "product_set_id": prod_set.id, "quantity": 1}
        )
        wiz.add_set()
        order_line = so.order_line.filtered(
            lambda x: x.product_id == prod_set.set_line_ids[0].product_id
        )
        order_line.ensure_one()
        self.assertEqual(order_line.discount, set_line.discount)

    def test_product_set_delete_in_wizard(self):
        products = self.so.order_line.product_id
        wizard = self._get_wiz()
        wizard.write({"product_set_line_ids": [(3, wizard.product_set_line_ids[0].id)]})
        products |= wizard.product_set_line_ids.product_id
        wizard.add_set()
        self.assertEqual(products, self.so.order_line.product_id)
        self.assertEqual(len(self.so.order_line), 3)

    def test_add_set_section(self):
        so = self.env.ref("sale.sale_order_6")
        base_line_ids = so.order_line
        count_lines = len(so.order_line)
        product_set_with_section = self.env.ref("product_set.product_set_services")
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
