# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase

from odoo.addons.sale_manual_delivery.hook import pre_init_hook


class TestPreInitHook(TransactionCase):
    """Non-regression tests for the ``pre_init_hook`` SQL update.

    The hook runs *before* the module is installed, so at hook time the
    ``manual_delivery`` field does not exist and no record in the database
    can have been created through this module. The test data therefore
    only uses standard sale/stock flows.

    Each test resets the columns of its own line right before calling the
    hook and reads them back through raw SQL, so existing data in the test
    database can neither pollute the assertions nor be polluted by them.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Pre-Init Hook Partner"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Pre-Init Hook Product",
                "type": "consu",
                "is_storable": True,
                "list_price": 10.0,
            }
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Test Pre-Init Hook Service",
                "type": "service",
                "list_price": 5.0,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 1000
        )

    def _create_order(self, product, qty):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
                            "price_unit": product.list_price,
                        },
                    )
                ],
            }
        )

    def _read_qty(self, line):
        """Read raw column values, bypassing the ORM compute trigger."""
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT qty_procured, qty_to_procure " "FROM sale_order_line WHERE id = %s",
            (line.id,),
        )
        return self.env.cr.fetchone()

    def _set_qty(self, line, qty_procured, qty_to_procure):
        """Force raw column values to simulate a given pre-hook state."""
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE sale_order_line "
            "SET qty_procured = %s, qty_to_procure = %s "
            "WHERE id = %s",
            (qty_procured, qty_to_procure, line.id),
        )
        self.env.invalidate_all()

    def test_pre_init_hook_fully_delivered(self):
        """Tout livré: standard order, picking validated for the full qty.

        Expected: qty_procured = ordered qty, qty_to_procure = 0.
        """
        order = self._create_order(self.product, qty=10)
        order.action_confirm()
        picking = order.picking_ids
        self.assertTrue(picking)
        picking.action_assign()
        picking.move_line_ids.write({"quantity": 10})
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        line = order.order_line

        self._set_qty(line, None, None)
        pre_init_hook(self.env)

        qty_procured, qty_to_procure = self._read_qty(line)
        self.assertEqual(qty_procured, 10.0)
        self.assertEqual(qty_to_procure, 0.0)

    def test_pre_init_hook_partially_delivered(self):
        """Partiellement livré: stock move qty manually reduced below the
        SOL qty (mimics a real-world partial state - cancelled partial
        moves, edited moves, etc. - using only standard flows).

        Expected: qty_procured = move qty, qty_to_procure = remaining.
        """
        order = self._create_order(self.product, qty=10)
        order.action_confirm()
        move = order.picking_ids.move_ids
        self.assertEqual(len(move), 1)
        move.product_uom_qty = 4
        line = order.order_line

        self._set_qty(line, None, None)
        pre_init_hook(self.env)

        qty_procured, qty_to_procure = self._read_qty(line)
        self.assertEqual(qty_procured, 4.0)
        self.assertEqual(qty_to_procure, 6.0)

    def test_pre_init_hook_nothing_delivered(self):
        """Rien livré: a service line has no stock_move at all.

        Order with two lines (one service, one storable) so the test
        observes the hook on both a no-move line and a control line:

        - The control line proves the hook's UPDATE actually ran.
        - The service line is set to a sentinel so we can see whether
          the hook touched it or not.
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.service.name,
                            "product_id": self.service.id,
                            "product_uom_qty": 5,
                            "product_uom": self.service.uom_id.id,
                            "price_unit": self.service.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 8,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
            }
        )
        order.action_confirm()
        service_line = order.order_line.filtered(
            lambda line: line.product_id == self.service
        )
        control_line = order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertFalse(service_line.move_ids)
        self.assertTrue(control_line.move_ids)

        self._set_qty(service_line, 42.0, 99.0)
        self._set_qty(control_line, None, None)

        pre_init_hook(self.env)

        # Service line: the current SQL updates *every* SOL (the inner-
        # join-on-self pattern doesn't filter), so the sentinel is
        # overwritten with qty_procured=0 and qty_to_procure=ordered.
        s_procured, s_to_procure = self._read_qty(service_line)
        self.assertEqual(s_procured, 0.0)
        self.assertEqual(s_to_procure, 5.0)
        # Control line: proves the hook actually executed its UPDATE.
        c_procured, c_to_procure = self._read_qty(control_line)
        self.assertEqual(c_procured, 8.0)
        self.assertEqual(c_to_procure, 0.0)
