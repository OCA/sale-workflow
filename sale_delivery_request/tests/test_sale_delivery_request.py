# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSaleDeliveryRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "list_price": 100.0,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "list_price": 200.0,
            }
        )
        cls.company = cls.env.company
        cls.company.delivery_request_expiration_days = 15
        cls.company.security_lead = 0

    def _create_sale_order(self, lines=None):
        """Create an SO with given lines [(product, qty), ...]"""
        if lines is None:
            lines = [(self.product1, 10), (self.product2, 5)]
        so = self.env["sale.order"].create({"partner_id": self.partner.id})
        for product, qty in lines:
            self.env["sale.order.line"].create(
                {
                    "order_id": so.id,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "price_unit": product.list_price,
                }
            )
        return so

    def _create_delivery_request(self, so):
        """Create a DR from an SO via the button action."""
        action = so.action_request_delivery_date()
        return self.env["sale.delivery.request"].browse(action["res_id"])

    # DR creation flow
    def test_00_create_delivery_request_from_so(self):
        """Creating a DR from SO populates lines correctly."""
        so = self._create_sale_order()
        dr = self._create_delivery_request(so)

        self.assertEqual(dr.state, "pending")
        self.assertEqual(dr.sale_order_id, so)
        self.assertEqual(len(dr.line_ids), 2)
        self.assertEqual(
            set(dr.line_ids.mapped("product_id")),
            {self.product1, self.product2},
        )

    def test_01_create_delivery_request_no_lines_raises(self):
        """Cannot create a DR from an SO with no eligible lines."""
        so = self.env["sale.order"].create({"partner_id": self.partner.id})
        # Add only a section line (display_type)
        self.env["sale.order.line"].create(
            {
                "order_id": so.id,
                "name": "Section",
                "display_type": "line_section",
            }
        )
        with self.assertRaises(UserError):
            so.action_request_delivery_date()

    def test_02_so_has_delivery_request_flag(self):
        """has_delivery_request is set after creating a DR."""
        so = self._create_sale_order()
        self.assertFalse(so.has_delivery_request)
        self._create_delivery_request(so)
        self.assertTrue(so.has_delivery_request)

    # DR confirmation and commitment_date
    def test_03_confirm_dr_sets_commitment_date_on_sol(self):
        """When a DR is confirmed, commitment_date is populated on SOLs."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=20)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        self.assertEqual(dr.state, "confirmed")
        sol = so.order_line.filtered(lambda x: not x.display_type)
        self.assertTrue(sol.commitment_date)
        self.assertTrue(sol.commitment_date_from_dr)

    def test_04_confirm_dr_without_dates_raises(self):
        """Cannot confirm a DR if lines don't have promised dates."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        with self.assertRaises(UserError):
            dr.action_confirm()

    def test_05_commitment_date_locked_after_dr(self):
        """commitment_date cannot be manually changed once set by a DR."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=20)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        sol = so.order_line.filtered(lambda x: not x.display_type)
        with self.assertRaises(UserError):
            sol.commitment_date = datetime.now() + timedelta(days=30)

    # SO confirmation with DR
    def test_06_so_confirm_with_valid_dr(self):
        """SO can be confirmed when DR is confirmed and not expired."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=20)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        so.action_confirm()
        self.assertEqual(so.state, "sale")

    def test_07_so_confirm_blocked_by_pending_dr(self):
        """SO confirmation is blocked if DR is still pending."""
        so = self._create_sale_order([(self.product1, 10)])
        self._create_delivery_request(so)

        with self.assertRaises(UserError):
            so.action_confirm()

    def test_08_so_confirm_creates_picking_with_scheduled_date(self):
        """After SO confirmation, picking scheduled_date matches commitment_date."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=20)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        so.action_confirm()
        self.assertTrue(so.picking_ids)
        sol = so.order_line.filtered(lambda x: not x.display_type)
        picking = so.picking_ids
        self.assertEqual(
            picking.scheduled_date.date(),
            sol.commitment_date.date(),
        )

    # Multiple DR lines (split) and picking dates
    def test_09_dr_split_creates_multiple_sols_and_pickings(self):
        """Split DR lines for the same SOL create separate SOLs and pickings."""
        so = self._create_sale_order([(self.product1, 20)])
        dr = self._create_delivery_request(so)

        line = dr.line_ids
        self.assertEqual(len(line), 1)
        self.assertEqual(line.quantity, 20)

        # Split: open wizard and split into 8 + 12
        action = line.action_split_quantity()
        wizard = (
            self.env[action["res_model"]]
            .with_context(**action["context"])
            .create({"split_qty": 8})
        )
        wizard.action_split()

        self.assertEqual(len(dr.line_ids), 2)
        sorted_lines = dr.line_ids.sorted("quantity")
        self.assertEqual(sorted_lines[0].quantity, 8)
        self.assertEqual(sorted_lines[1].quantity, 12)

        # Assign different dates
        date1 = date.today() + timedelta(days=10)
        date2 = date.today() + timedelta(days=25)
        sorted_lines[0].promised_date_absolute = date1
        sorted_lines[1].promised_date_absolute = date2

        dr.action_confirm()
        so.action_confirm()

        self.assertEqual(len(so.picking_ids), 2)
        sorted_pickings = so.picking_ids.sorted("scheduled_date")
        self.assertNotEqual(
            sorted_pickings[0].scheduled_date.date(),
            sorted_pickings[1].scheduled_date.date(),
        )

    # Expiration and reconfirmation flow
    def test_10_cron_expires_confirmed_requests(self):
        """Cron marks confirmed DRs as expired when past expiration date."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=5)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        self.assertEqual(dr.state, "confirmed")

        # Simulate expiration: set expiration_date to yesterday
        dr.expiration_date = date.today() - timedelta(days=1)
        self.env["sale.delivery.request"]._cron_check_expiration()

        self.assertEqual(dr.state, "expired")

    def test_11_expired_dr_blocks_so_and_creates_priority_request(self):
        """
        Confirming SO with all DRs expired creates a priority request
        and blocks SO confirmation.
        """
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=5)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        # Force expire
        dr.expiration_date = date.today() - timedelta(days=1)
        self.env["sale.delivery.request"]._cron_check_expiration()
        self.assertEqual(dr.state, "expired")

        # Attempt to confirm SO — should return notification, not confirm
        result = so.action_confirm()
        self.assertEqual(result.get("type"), "ir.actions.client")
        self.assertEqual(result.get("tag"), "display_notification")
        self.assertNotEqual(so.state, "sale")

        # A new priority request should exist
        new_dr = so.delivery_request_ids.filtered(
            lambda r: r.is_priority_request and r.state == "pending"
        )
        self.assertEqual(len(new_dr), 1)

    def test_12_create_priority_request_only_from_expired(self):
        """_create_priority_request raises if the DR is not expired."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=5)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        with self.assertRaises(UserError):
            dr._create_priority_request()

    def test_13_priority_request_confirm_auto_confirms_so(self):
        """Confirming a priority DR auto-confirms the SO."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=5)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        # Force expire
        dr.expiration_date = date.today() - timedelta(days=1)
        self.env["sale.delivery.request"]._cron_check_expiration()

        # Trigger priority creation via SO confirm attempt
        so.action_confirm()
        priority_dr = so.delivery_request_ids.filtered(
            lambda r: r.is_priority_request and r.state == "pending"
        )
        self.assertTrue(priority_dr)

        # Confirm the priority DR
        new_promised = date.today() + timedelta(days=15)
        priority_dr.line_ids.write({"promised_date_absolute": new_promised})
        priority_dr.action_confirm()

        self.assertEqual(priority_dr.state, "confirmed")
        self.assertEqual(so.state, "sale")

    # Manual expiration
    def test_14_manual_set_expired(self):
        """action_set_expired changes state to expired."""
        so = self._create_sale_order([(self.product1, 10)])
        dr = self._create_delivery_request(so)

        promised = date.today() + timedelta(days=5)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()

        dr.action_set_expired()
        self.assertEqual(dr.state, "expired")

    # has_valid_delivery_request
    def test_15_has_valid_delivery_request(self):
        """has_valid_delivery_request reflects confirmed DR state."""
        so = self._create_sale_order([(self.product1, 10)])
        self.assertFalse(so.has_valid_delivery_request)

        dr = self._create_delivery_request(so)
        self.assertFalse(so.has_valid_delivery_request)

        promised = date.today() + timedelta(days=20)
        dr.line_ids.write({"promised_date_absolute": promised})
        dr.action_confirm()
        self.assertTrue(so.has_valid_delivery_request)

        dr.action_set_expired()
        self.assertFalse(so.has_valid_delivery_request)
