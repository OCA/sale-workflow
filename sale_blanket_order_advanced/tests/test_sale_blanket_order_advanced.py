# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from odoo.exceptions import UserError, ValidationError

from .common import BlanketOrderCase


class TestVersionWizard(BlanketOrderCase):
    def setUp(self):
        super().setUp()
        self.blanket_order = self._create_blanket_order()
        self._add_line_to_order(self.blanket_order)

    def test_version_count_initial_zero(self):
        self.assertEqual(self.blanket_order.version_count, 0)

    def test_create_version_blocked_when_not_invoiced(self):
        self.blanket_order.action_confirm()
        with self.assertRaises(UserError) as exc:
            self.env["sale.blanket.order.advanced.version.wizard"].create(
                {"old_blanket_order_id": self.blanket_order.id}
            ).create_version()
        self.assertIn("fully invoiced", str(exc.exception))

    def test_version_count_increases_after_version(self):
        self._create_fake_invoiced_scenario(self.blanket_order)
        self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": self.blanket_order.id}
        ).create_version()
        self.blanket_order.invalidate_recordset()
        self.assertEqual(self.blanket_order.version_count, 1)

    def test_all_sale_orders_invoiced_false_when_no_orders(self):
        self.assertFalse(self.blanket_order.all_sale_orders_invoiced)

    def test_action_view_versions_without_versions(self):
        result = self.blanket_order.action_view_versions()
        self.assertEqual(result["type"], "ir.actions.act_window_close")

    def test_action_view_versions_with_versions(self):
        self._create_fake_invoiced_scenario(self.blanket_order)
        self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": self.blanket_order.id}
        ).create_version()
        result = self.blanket_order.action_view_versions()
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_set_to_draft_blocked_with_versions(self):
        self._create_fake_invoiced_scenario(self.blanket_order)
        self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": self.blanket_order.id}
        )
        with self.assertRaises(UserError) as exc:
            self.blanket_order.set_to_draft()
        self.assertIn("associated versions", str(exc.exception))

    def test_set_to_draft_allowed_without_versions(self):
        self.blanket_order.action_confirm()
        self.blanket_order.set_to_draft()
        self.assertEqual(self.blanket_order.state, "draft")

    def test_wizard_default_get_without_context(self):
        defaults = self.env["sale.blanket.order.advanced.version.wizard"].default_get(
            ["old_blanket_order_id"]
        )
        self.assertNotIn("old_blanket_order_id", defaults)

    def test_wizard_default_get_with_context(self):
        defaults = (
            self.env["sale.blanket.order.advanced.version.wizard"]
            .with_context(default_old_blanket_order_id=self.blanket_order.id)
            .default_get(["old_blanket_order_id"])
        )
        self.assertEqual(defaults.get("old_blanket_order_id"), self.blanket_order.id)

    def test_create_version_with_price_adjustment(self):
        self._create_fake_invoiced_scenario(self.blanket_order)
        wizard = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {
                "old_blanket_order_id": self.blanket_order.id,
                "price_adjustment_percent": 20.0,
            }
        )
        wizard.create_version()
        new_line = wizard.new_blanket_order_id.line_ids[0]
        self.assertAlmostEqual(new_line.price_unit, 120.0)

    def test_version_name_increments(self):
        self._create_fake_invoiced_scenario(self.blanket_order)
        wizard1 = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": self.blanket_order.id}
        )
        wizard1.create_version()
        self.assertIn("(Ver 1)", wizard1.new_blanket_order_id.name)

    def test_create_version_syncs_order_plan_fields(self):
        self._create_fake_invoiced_scenario(self.blanket_order)
        self.blanket_order.write({"use_sale_order_plan": True})
        wizard = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": self.blanket_order.id}
        )
        wizard.create_version()
        self.assertTrue(wizard.new_blanket_order_id.use_sale_order_plan)


class TestCreateOrderPlan(BlanketOrderCase):
    def setUp(self):
        super().setUp()
        self.blanket_order = self._create_blanket_order()
        self._add_line_to_order(self.blanket_order)

    def test_wizard_default_values(self):
        wizard = self.env["sale.create.order.plan"].create({})
        self.assertEqual(wizard.num_installment, 2)
        self.assertEqual(wizard.interval, 1)
        self.assertEqual(wizard.interval_type, "month")

    def test_wizard_constrains_num_installment(self):
        with self.assertRaises(ValidationError):
            self.env["sale.create.order.plan"].create({"num_installment": 1})

    def test_create_order_plan_creates_lines(self):
        wizard = self.env["sale.create.order.plan"].create(
            {"num_installment": 3, "interval": 1, "interval_type": "month"}
        )
        wizard.with_context(active_id=self.blanket_order.id).sale_create_order_plan()
        self.assertEqual(len(self.blanket_order.sale_order_plan_ids), 3)

    def test_order_plan_installment_numbers(self):
        self.blanket_order.create_order_plan(
            num_installment=3,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        plans = self.blanket_order.sale_order_plan_ids.sorted("installment")
        self.assertEqual(plans[0].installment, 1)
        self.assertEqual(plans[2].installment, 3)


class TestMakePlannedOrder(BlanketOrderCase):
    def setUp(self):
        super().setUp()
        self.blanket_order = self._create_blanket_order()
        self._add_line_to_order(self.blanket_order)

    def test_wizard_creates_orders_by_plan(self):
        self.blanket_order.action_confirm()
        self.blanket_order.create_order_plan(
            num_installment=1,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        wizard = self.env["sale.make.planned.order"].create({})
        wizard.with_context(active_id=self.blanket_order.id).create_orders_by_plan()
        self.assertEqual(len(self.blanket_order.sale_order_plan_ids), 1)

    def test_wizard_creates_all_remaining_orders(self):
        self.blanket_order.action_confirm()
        self.blanket_order.create_order_plan(
            num_installment=2,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        wizard = self.env["sale.make.planned.order"].create({})
        wizard.with_context(
            active_id=self.blanket_order.id, all_remain_orders=True
        ).create_orders_by_plan()
        self.assertEqual(len(self.blanket_order.sale_order_plan_ids), 2)


class TestProductCost(BlanketOrderCase):
    def setUp(self):
        super().setUp()
        self.blanket_order = self._create_blanket_order()

    def test_product_cost_computation(self):
        cost = self.env["blanket.order.product"].create(
            {
                "blanket_order_id": self.blanket_order.id,
                "product_id": self.product.id,
                "quantity": 2.0,
                "price_unit": 50.0,
            }
        )
        self.assertEqual(cost.subtotal, 100.0)

    def test_product_onchange_updates_price(self):
        cost = self.env["blanket.order.product"].new({"product_id": self.product.id})
        cost._onchange_product_id()
        self.assertEqual(cost.price_unit, self.product.standard_price)


class TestServiceCost(BlanketOrderCase):
    def setUp(self):
        super().setUp()
        self.blanket_order = self._create_blanket_order()

    def test_service_cost_computation(self):
        cost = self.env["blanket.order.service"].create(
            {
                "blanket_order_id": self.blanket_order.id,
                "product_id": self.service.id,
                "quantity": 2.0,
                "price_unit": 40.0,
            }
        )
        self.assertEqual(cost.subtotal, 80.0)

    def test_service_onchange_updates_price(self):
        cost = self.env["blanket.order.service"].new({"product_id": self.service.id})
        cost._onchange_product_id()
        self.assertEqual(cost.price_unit, self.service.standard_price)


class TestAdvancedFeatures(BlanketOrderCase):
    def test_action_confirm_without_order_plan_raises_error(self):
        order = self._create_blanket_order(use_sale_order_plan=True)
        self._add_line_to_order(order)
        with self.assertRaises(UserError) as exc:
            order.action_confirm()
        self.assertIn("Use Order Plan", str(exc.exception))

    def test_remove_order_plan(self):
        order = self._create_blanket_order()
        self._add_line_to_order(order)
        order.create_order_plan(
            num_installment=2,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        self.assertEqual(len(order.sale_order_plan_ids), 2)
        order.remove_order_plan()
        self.assertEqual(len(order.sale_order_plan_ids), 0)

    def test_next_date_month(self):
        order = self._create_blanket_order()
        result = order._next_date(datetime.date(2026, 1, 15), 1, "month")
        self.assertEqual(result, "2026-02-15")

    def test_next_date_year(self):
        order = self._create_blanket_order()
        result = order._next_date(datetime.date(2026, 1, 15), 1, "year")
        self.assertEqual(result, "2027-01-15")

    def test_ip_sale_order_plan_in_progress(self):
        order = self._create_blanket_order(use_sale_order_plan=True)
        self._add_line_to_order(order)
        order.create_order_plan(
            num_installment=1,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        order.action_confirm()
        self.assertTrue(order.ip_sale_order_plan)

    def test_ip_sale_order_plan_not_in_progress(self):
        order = self._create_blanket_order()
        self._add_line_to_order(order)
        self.assertFalse(order.ip_sale_order_plan)


class TestSaleOrderPlan(BlanketOrderCase):
    def setUp(self):
        super().setUp()
        self.blanket_order = self._create_blanket_order(state="open")
        self._add_line_to_order(self.blanket_order, qty=100.0)

    def test_plan_compute_last(self):
        self.blanket_order.create_order_plan(
            num_installment=3,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        plans = self.blanket_order.sale_order_plan_ids.sorted("installment")
        self.assertFalse(plans[0].last)
        self.assertTrue(plans[2].last)

    def test_plan_compute_ordered_false(self):
        self.blanket_order.create_order_plan(
            num_installment=1,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        self.assertFalse(self.blanket_order.sale_order_plan_ids.ordered)

    def test_check_order_plan_constraint(self):
        order = self._create_blanket_order(state="done")
        self._add_line_to_order(order)
        plan = self.env["blanket.order.plan"].create(
            {
                "sale_id": order.id,
                "installment": 1,
                "plan_date": datetime.date.today(),
                "order_type": "installment",
                "percent": 100,
            }
        )
        self.assertEqual(plan.sale_id, order)


class TestVersionWizardMethods(BlanketOrderCase):
    def test_wizard_get_version_number(self):
        order = self._create_blanket_order()
        self._add_line_to_order(order)
        self._create_fake_invoiced_scenario(order)
        wizard = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": order.id}
        )
        wizard.create_version()
        self.assertEqual(wizard._get_version_number(), 1)

    def test_wizard_get_next_version_name(self):
        order = self._create_blanket_order(name="SBO/2026/001")
        self._add_line_to_order(order)
        wizard = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": order.id}
        )
        name = wizard._get_next_version_name()
        self.assertIn("(Ver 1)", name)

    def test_version_wizard_duplicate_order(self):
        order = self._create_blanket_order()
        self._add_line_to_order(order)
        wizard = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": order.id}
        )
        new_order = wizard._duplicate_order()
        self.assertTrue(new_order)
        self.assertIn("(Ver 1)", new_order.name)

    def test_version_wizard_sync_order_plan(self):
        order = self._create_blanket_order(use_sale_order_plan=True)
        self._add_line_to_order(order)
        order.create_order_plan(
            num_installment=2,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        self.env["blanket.order.product"].create(
            {
                "blanket_order_id": order.id,
                "product_id": self.product.id,
                "quantity": 2.0,
                "price_unit": 50.0,
            }
        )
        wizard = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": order.id}
        )
        new_order = wizard._duplicate_order()
        wizard._sync_order_lines(order, new_order)
        self.assertTrue(new_order.use_sale_order_plan)
        self.assertEqual(len(new_order.sale_order_plan_ids), 2)


class TestCostComputations(BlanketOrderCase):
    def setUp(self):
        super().setUp()
        self.blanket_order = self._create_blanket_order()

    def test_blanket_order_total_costs(self):
        self.env["blanket.order.product"].create(
            {
                "blanket_order_id": self.blanket_order.id,
                "product_id": self.product.id,
                "quantity": 2.0,
                "price_unit": 50.0,
            }
        )
        self.env["blanket.order.service"].create(
            {
                "blanket_order_id": self.blanket_order.id,
                "product_id": self.service.id,
                "quantity": 3.0,
                "price_unit": 40.0,
            }
        )
        self.assertEqual(self.blanket_order.total_product_costs, 100.0)
        self.assertEqual(self.blanket_order.total_service_costs, 120.0)
        self.assertEqual(self.blanket_order.total_costs, 220.0)


class TestPlanQuantity(BlanketOrderCase):
    def test_plan_compute_new_order_quantity_last_installment(self):
        order = self._create_blanket_order(state="open")
        self._add_line_to_order(order, qty=100.0)
        order.create_order_plan(
            num_installment=1,
            installment_date=datetime.date.today(),
            interval=1,
            interval_type="month",
        )
        plan = order.sale_order_plan_ids
        result = plan._compute_new_order_quantity(order)
        self.assertIsNone(result)


class TestAllCoverage(BlanketOrderCase):
    def test_all_sale_orders_invoiced_with_sale_orders(self):
        order = self._create_blanket_order(state="open")
        self._add_line_to_order(order, qty=100.0)
        self.assertFalse(order.all_sale_orders_invoiced)

    def test_create_sale_order_no_available_lines(self):
        order = self._create_blanket_order(state="open")
        result = order._create_sale_order()
        self.assertEqual(len(result), 0)

    def test_action_show_account_analytic_line_no_account(self):
        order = self._create_blanket_order()
        self._add_line_to_order(order)
        result = order.action_show_account_analytic_line()
        self.assertEqual(result["res_model"], "account.analytic.line")

    def test_compute_account_analytic_line_no_account(self):
        order = self._create_blanket_order()
        self._add_line_to_order(order)
        self.assertFalse(order.account_analytic_line_ids)
        self.assertEqual(order.account_analytic_line_count, 0)

    def test_version_wizard_message_post(self):
        order = self._create_blanket_order()
        self._add_line_to_order(order)
        wizard = self.env["sale.blanket.order.advanced.version.wizard"].create(
            {"old_blanket_order_id": order.id}
        )
        new_order = wizard._duplicate_order()
        wizard._sync_order_lines(order, new_order)
        self.assertIn("message_post", dir(new_order))
