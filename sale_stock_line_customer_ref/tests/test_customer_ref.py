# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.tests.common import Form, SavepointCase


class TestSaleLineCustomerRef(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.delivery_steps = "pick_pack_ship"
        cls.product = cls.env.ref("product.consu_delivery_01")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.order = cls._create_order()
        cls.order.action_confirm()
        cls.pkg_model = cls.env["stock.quant.package"]

    @classmethod
    def _create_order(cls):
        # Create a SO with 4 lines sharing the same product but with 2 different
        # customer references.
        with Form(cls.env["sale.order"]) as form:
            form.partner_id = cls.env.ref("base.res_partner_1")
            for i in range(4):
                with form.order_line.new() as line:
                    line.product_id = cls.product
                    line.customer_ref = f"TEST_{i % 2}"
                    line.product_uom = cls.product.uom_id
                    line.product_uom_qty = 1
            order = form.save()
            return order

    @classmethod
    def _update_qty_in_location(
        cls, location, product, quantity, package=None, lot=None
    ):
        quants = cls.env["stock.quant"]._gather(
            product, location, lot_id=lot, package_id=package, strict=True
        )
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(
            product, location, quantity, package_id=package, lot_id=lot
        )

    @classmethod
    def _get_pick(cls, order):
        return order.picking_ids.filtered(lambda x: not x.move_lines.move_orig_ids)

    @classmethod
    def _get_pack(cls, order):
        return cls._get_pick(order).move_lines.move_dest_ids.picking_id

    def test_customer_ref(self):
        # Ship moves can't be merged anyway in std Odoo as they belong to
        # different SO lines, but chained moves not linked directly to
        # the SO lines can still be merged based on the customer reference.
        self.assertEqual(len(self.order.order_line), 4)
        self.assertEqual(len(self.order.order_line.move_ids), 4)
        self._test_customer_ref()

    def _test_customer_ref(self):
        # Check customer ref. among chained moves of all SO lines
        for i in range(4):
            expected_ref = f"TEST_{i % 2}"
            order_line = self.order.order_line[i]
            order_lines_same_ref = self.order.order_line.filtered_domain(
                [("customer_ref", "=", expected_ref)]
            )
            self.assertEqual(order_line.customer_ref, expected_ref)
            # Customer reference is propagated on the ship move
            move_ship = order_line.move_ids
            self.assertEqual(move_ship.customer_ref_sale_line_id, order_line)
            self.assertEqual(move_ship.customer_ref, expected_ref)
            self.assertEqual(move_ship.product_uom_qty, 1)
            # And on the pack and pick moves have been merged based on
            # the propagated customer reference.
            move_pack = move_ship.move_orig_ids
            self.assertIn(move_pack.customer_ref_sale_line_id, order_lines_same_ref)
            self.assertEqual(move_pack.customer_ref, expected_ref)
            self.assertEqual(move_pack.product_uom_qty, 2)
            move_pick = move_pack.move_orig_ids
            self.assertIn(move_pick.customer_ref_sale_line_id, order_lines_same_ref)
            self.assertEqual(move_pick.customer_ref, expected_ref)
            self.assertEqual(move_pick.product_uom_qty, 2)

    def test_has_customer_ref(self):
        for picking in self.order.picking_ids:
            self.assertTrue(picking.has_customer_ref)

    def test_package_ref(self):
        self._update_qty_in_location(self.stock_loc, self.product, 10)
        picking = self._get_pick(self.order)
        picking.action_assign()
        expected = ["TEST_0", "TEST_1"]
        self.assertEqual(picking.move_line_ids.mapped("customer_ref"), expected)
        pkg1 = self.pkg_model.create({"name": "TEST-REF-1"})
        pkg2 = self.pkg_model.create({"name": "TEST-REF-2"})
        picking.move_line_ids[0].result_package_id = pkg1
        picking.move_line_ids[1].result_package_id = pkg2
        packages = picking.move_line_ids.result_package_id.sorted("name")
        packages.invalidate_cache()

        self.assertEqual(packages.mapped("customer_ref"), ["TEST_0", "TEST_1"])
        picking.move_line_ids.filtered(
            lambda x: x.result_package_id == pkg2
        ).result_package_id = False
        packages.invalidate_cache()
        self.assertEqual(packages.mapped("customer_ref"), ["TEST_0", False])

    def test_package_ref_concat(self):
        self._update_qty_in_location(self.stock_loc, self.product, 10)
        picking = self._get_pick(self.order)
        picking.action_assign()
        expected = ["TEST_0", "TEST_1"]
        self.assertEqual(picking.move_line_ids.mapped("customer_ref"), expected)
        pkg1 = self.pkg_model.create({"name": "TEST-REF-1"})
        self.pkg_model.create({"name": "TEST-REF-2"})
        picking.move_line_ids.result_package_id = pkg1
        packages = picking.move_line_ids.result_package_id.sorted("name")
        packages.invalidate_cache()

        self.assertEqual(packages.mapped("customer_ref"), ["TEST_0, TEST_1"])
        picking.move_line_ids.result_package_id = False
        packages.invalidate_cache()
        self.assertEqual(packages.mapped("customer_ref"), [False])
