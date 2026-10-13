# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestSaleInvoicePlanAllocation(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        unit = cls.env.ref("uom.product_uom_unit")
        product_categ = cls.company_data["product_category"]
        cls.products = cls.env["product.product"].create(
            [
                {
                    "name": "Product A",
                    "type": "consu",
                    "invoice_policy": "order",
                    "list_price": 100.0,
                    "uom_id": unit.id,
                    "uom_po_id": unit.id,
                    "taxes_id": [Command.clear()],
                    "categ_id": product_categ.id,
                },
                {
                    "name": "Product B",
                    "type": "consu",
                    "invoice_policy": "order",
                    "list_price": 200.0,
                    "uom_id": unit.id,
                    "uom_po_id": unit.id,
                    "taxes_id": [Command.clear()],
                    "categ_id": product_categ.id,
                },
                {
                    "name": "Product C",
                    "type": "consu",
                    "invoice_policy": "order",
                    "list_price": 300.0,
                    "uom_id": unit.id,
                    "uom_po_id": unit.id,
                    "taxes_id": [Command.clear()],
                    "categ_id": product_categ.id,
                },
            ]
        )

    def _create_order(
        self,
        method="manual",
        products=None,
        quantity=5.0,
        num_installment=5,
        advance=False,
    ):
        products = products or self.products
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "use_invoice_plan": True,
                "invoice_plan_method": method,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                            "price_unit": product.list_price,
                        }
                    )
                    for product in products
                ],
            }
        )
        order.create_invoice_plan(
            num_installment,
            fields.Date.today(),
            1,
            "month",
            advance,
        )
        return order

    def _create_sequential_order(self, lines, advance=False):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "use_invoice_plan": True,
                "invoice_plan_method": "sequential",
                "order_line": [
                    Command.create(
                        {
                            "product_id": line["product"].id,
                            "product_uom_qty": line["qty"],
                            "price_unit": line["product"].list_price,
                            "invoice_plan_group": line.get("group", 1),
                        }
                    )
                    for line in lines
                ],
            }
        )
        order.create_invoice_plan(1, fields.Date.today(), 1, "month", advance)
        return order

    def _set_allocation(self, plan, sale_line, quantity):
        plan.allocation_ids.filtered(
            lambda allocation: allocation.sale_line_id == sale_line
        ).quantity = quantity

    def _create_invoices(self, order, all_remaining=True):
        wizard = self.env["sale.make.planned.invoice"].create({})
        return wizard.with_context(
            active_id=order.id,
            active_ids=order.ids,
            all_remain_invoices=all_remaining,
        ).create_invoices_by_plan()

    def test_01_non_allocation_process(self):
        """Proportional remains standard; a disabled plan ignores its stale method."""
        proportional = self._create_order(method="proportional")
        self.assertFalse(proportional.invoice_plan_ids.allocation_ids)

        proportional.action_confirm()
        self._create_invoices(proportional)

        self.assertEqual(len(proportional.invoice_ids), 5)
        for invoice in proportional.invoice_ids:
            self.assertEqual(invoice.amount_untaxed, 600.0)
            self.assertEqual(
                sorted(
                    invoice.invoice_line_ids.filtered("product_id").mapped("quantity")
                ),
                [1.0, 1.0, 1.0],
            )

        disabled = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "use_invoice_plan": False,
                "invoice_plan_method": "manual",
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.products[0].id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
        disabled.action_confirm()
        self.assertEqual(disabled.state, "sale")

    def test_02_manual_allocation_process(self):
        """Create, validate, edit, confirm, and invoice a manual allocation."""
        order = self._create_order()
        plans = order.invoice_plan_ids.sorted("installment")
        line_a, line_b, line_c = order.order_line

        action = plans[:1].action_open_allocation()
        self.assertEqual(
            action["view_id"],
            self.env.ref(
                "sale_invoice_plan_allocation.view_sale_invoice_plan_form_allocation"
            ).id,
        )

        # The user cannot confirm an unfinished allocation or change its method.
        with self.assertRaisesRegex(ValidationError, "has no allocated quantity"):
            order.action_confirm()
        with self.assertRaisesRegex(UserError, "Remove the invoice plan first"):
            order.invoice_plan_method = "sequential"

        quantities = [
            (0, 0, 2),
            (2, 2, 0),
            (1, 1, 1),
            (1, 1, 1),
            (1, 1, 1),
        ]
        for plan, plan_quantities in zip(plans, quantities, strict=True):
            for sale_line, quantity in zip(
                order.order_line, plan_quantities, strict=True
            ):
                self._set_allocation(plan, sale_line, quantity)

        with self.assertRaisesRegex(ValidationError, "must be fully allocated"):
            plans[0].allocation_ids.filtered(
                lambda a: a.sale_line_id == line_c
            ).quantity = 0
            plans[0].allocation_ids.filtered(
                lambda a: a.sale_line_id == line_a
            ).quantity = 2
            order.action_confirm()
        self.assertEqual(plans[0].allocated_amount, 200.0)

        plans[0].allocation_ids.filtered(
            lambda a: a.sale_line_id == line_a
        ).quantity = 0
        plans[0].allocation_ids.filtered(
            lambda a: a.sale_line_id == line_c
        ).quantity = 2

        self.assertEqual(plans.mapped("allocated_amount"), [600.0] * 5)
        action = order.action_view_invoice_plan_allocations()
        self.assertEqual(action["res_model"], "sale.invoice.plan.allocation")
        self.assertEqual(action["domain"], [("sale_id", "=", order.id)])

        order.action_confirm()
        self._create_invoices(order)

        self.assertEqual(len(order.invoice_ids), 5)
        for plan, expected_quantities in zip(plans, quantities, strict=True):
            invoice = plan.invoice_move_ids
            actual_quantities = {
                line.sale_line_ids.id: line.quantity
                for line in invoice.invoice_line_ids.filtered("product_id")
            }
            expected = {
                sale_line.id: quantity
                for sale_line, quantity in zip(
                    (line_a, line_b, line_c), expected_quantities, strict=True
                )
                if quantity
            }
            self.assertEqual(len(invoice), 1)
            self.assertEqual(invoice.amount_untaxed, 600.0)
            self.assertEqual(actual_quantities, expected)

    def test_03_manual_even_split_process(self):
        """Bootstrap, reset, and rebalance remaining manual quantities."""
        order = self._create_order(products=self.products[0])
        plans = order.invoice_plan_ids.sorted("installment")
        plans[0].allocation_ids.quantity = 5.0

        order.action_allocate_evenly()

        self.assertEqual(plans.allocation_ids.mapped("quantity"), [1.0] * 5)
        self.assertFalse(plans.filtered("amount_to_allocate"))
        order.action_confirm()
        self._create_invoices(order, all_remaining=False)

        # Rebalancing after the first invoice distributes only the remainder.
        order.action_allocate_evenly()
        self.assertEqual(sum(plans.allocation_ids.mapped("quantity")), 5.0)
        self.assertEqual(
            plans.filtered(lambda plan: not plan.invoiced).allocation_ids.mapped(
                "quantity"
            ),
            [1.0] * 4,
        )
        self._create_invoices(order)
        self.assertEqual(len(order.invoice_ids), 5)

        # UoM/currency rounding can preserve quantity while leaving amount balance.
        rounded = self._create_order(
            products=self.products[0], quantity=5.0, num_installment=3
        )
        rounded.action_allocate_evenly()
        self.assertEqual(
            sum(rounded.invoice_plan_ids.allocation_ids.mapped("quantity")), 5.0
        )
        self.assertTrue(rounded.invoice_plan_ids.filtered("amount_to_allocate"))

    def test_04_delivery_policy_process(self):
        """A plan cannot invoice more than the delivered quantity."""
        delivery_product = self.products[0]
        delivery_product.invoice_policy = "delivery"
        order = self._create_order(products=delivery_product)
        order.invoice_plan_ids.allocation_ids.quantity = 1.0
        order.action_confirm()

        with self.assertRaisesRegex(ValidationError, "available to invoice"):
            self._create_invoices(order, all_remaining=False)

    def test_05_advance_plan_process(self):
        """Advance plans and generated down-payment lines never use allocations."""
        for method in ("manual", "sequential"):
            with self.subTest(method=method):
                if method == "manual":
                    order = self._create_order(
                        products=self.products[0],
                        quantity=2.0,
                        num_installment=2,
                        advance=True,
                    )
                    order.invoice_plan_ids.filtered(
                        lambda plan: plan.invoice_type == "installment"
                    ).allocation_ids.quantity = 1.0
                else:
                    order = self._create_sequential_order(
                        [{"product": self.products[0], "qty": 2, "group": 1}],
                        advance=True,
                    )

                advance_plan = order.invoice_plan_ids.filtered(
                    lambda plan: plan.invoice_type == "advance"
                )
                self.assertEqual(len(advance_plan), 1)
                self.assertFalse(advance_plan.allocation_ids)
                with self.assertRaisesRegex(ValidationError, "fill percentage"):
                    with self.env.cr.savepoint():
                        order.action_confirm()

                advance_plan.percent = 10
                order.action_confirm()
                self._create_invoices(order)

                self.assertEqual(len(order.invoice_ids), 3)
                self.assertEqual(
                    sum(
                        order.invoice_ids.invoice_line_ids.filtered(
                            lambda line: line.product_id == self.products[0]
                        ).mapped("quantity")
                    ),
                    2.0,
                )
                self.assertFalse(
                    order.order_line.filtered("is_downpayment")
                    & order.invoice_plan_ids.allocation_ids.sale_line_id
                )

    def test_06_sequential_allocation_process(self):
        """Build groups, validate overrides, confirm, and invoice the schedule."""
        # Group 2 deliberately appears first to verify numeric group ordering.
        order = self._create_sequential_order(
            [
                {"product": self.products[0], "qty": 2, "group": 2},
                {"product": self.products[1], "qty": 2, "group": 1},
                {"product": self.products[2], "qty": 1, "group": 1},
            ]
        )
        plans = order.invoice_plan_ids.sorted("installment")
        line_a, line_b, line_c = order.order_line

        self.assertEqual(len(plans), 4)
        self.assertEqual(plans[0].allocation_ids.sale_line_id, line_b + line_c)
        self.assertEqual(plans[1].allocation_ids.sale_line_id, line_b)
        self.assertEqual(plans[2:].allocation_ids.sale_line_id, line_a)
        self.assertEqual(len(plans.allocation_ids), 5)
        self.assertEqual(plans.mapped("amount"), [500.0, 200.0, 100.0, 100.0])
        self.assertEqual(plans.mapped("amount_to_allocate"), [0.0] * 4)

        # Totals are an invariant, while valid per-installment overrides remain open.
        plans[3].allocation_ids.quantity = 2.0
        with self.assertRaisesRegex(ValidationError, "must equal the ordered"):
            order.action_confirm()
        plans[2].allocation_ids.quantity = 1.5
        plans[3].allocation_ids.quantity = 0.5

        order.action_confirm()
        self._create_invoices(order)

        self.assertEqual(len(order.invoice_ids), 4)
        self.assertEqual(
            [
                sorted(
                    plan.invoice_move_ids.invoice_line_ids.filtered(
                        "product_id"
                    ).mapped("quantity")
                )
                for plan in plans
            ],
            [[1.0, 1.0], [1.0], [1.5], [0.5]],
        )

    def test_07_sequential_validation_and_wizard_process(self):
        """Reject invalid inputs and derive the installment count in the wizard."""
        with self.assertRaisesRegex(ValidationError, "positive quantities"):
            self._create_sequential_order(
                [{"product": self.products[0], "qty": 0, "group": 1}]
            )
        with self.assertRaisesRegex(ValidationError, "integer quantities"):
            self._create_sequential_order(
                [{"product": self.products[0], "qty": 1.5, "group": 1}]
            )

        empty = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "use_invoice_plan": True,
                "invoice_plan_method": "sequential",
            }
        )
        with self.assertRaisesRegex(ValidationError, "at least one invoiceable"):
            empty.create_invoice_plan(1, fields.Date.today(), 1, "month", False)

        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "use_invoice_plan": True,
                "invoice_plan_method": "sequential",
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.products[0].id,
                            "product_uom_qty": 3,
                            "invoice_plan_group": 2,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.products[1].id,
                            "product_uom_qty": 2,
                            "invoice_plan_group": 1,
                        }
                    ),
                ],
            }
        )
        wizard = (
            self.env["sale.create.invoice.plan"]
            .with_context(active_id=order.id, active_ids=order.ids)
            .create({})
        )
        self.assertEqual(wizard.parent_invoice_plan_method, "sequential")
        self.assertEqual(wizard.num_installment, 5)
        wizard.sale_create_invoice_plan()
        self.assertEqual(len(order.invoice_plan_ids), 5)

    def test_08_sequential_partial_invoice_and_rebuild_process(self):
        """Rebuild open plans safely and revalidate edits after a partial invoice."""
        order = self._create_sequential_order(
            [{"product": self.products[0], "qty": 2, "group": 1}]
        )
        plans = order.invoice_plan_ids.sorted("installment")
        order.action_confirm()
        self._create_invoices(order, all_remaining=False)

        plans[1].action_prepare_allocations()
        self.assertTrue(plans[0].invoiced)
        self.assertEqual(plans.mapped("allocation_ids.quantity"), [1.0, 1.0])

        plans[1].allocation_ids.quantity = 2.0
        with self.assertRaisesRegex(ValidationError, "must equal the ordered"):
            self._create_invoices(order, all_remaining=False)
        plans[1].allocation_ids.quantity = 1.0

        # A changed SO quantity requiring another installment is rejected before reset.
        order.order_line.product_uom_qty = 3
        with self.assertRaisesRegex(ValidationError, "requires 3 installments"):
            plans[1].action_prepare_allocations()
        self.assertEqual(plans[1].allocation_ids.quantity, 1.0)
