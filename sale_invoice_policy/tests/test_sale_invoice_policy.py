# Copyright 2017 Acsone SA/NV (http://www.acsone.eu)
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import new_test_user

from .common import SaleInvoicePolicyCommon


class TestSaleOrderInvoicePolicy(SaleInvoicePolicyCommon):
    def test_01_ordered_quantities_real_invoice(self):
        order = self._create_order(
            "order",
            [{"product_id": self.product_ordered_price.id, "product_uom_qty": 5.0}],
        )
        self.assertEqual(order.order_line.qty_to_invoice, 0.0)
        order.action_confirm()
        invoice = order._create_invoices()
        invoice.action_post()
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.invoice_line_ids.quantity, 5.0)
        self.assertEqual(invoice.amount_untaxed, 100.0)
        self.assertEqual(invoice.amount_total, 100.0)
        self.assertEqual(order.order_line.qty_invoiced, 5.0)
        done_pickings = 0
        for picking in order.picking_ids:
            if picking.state == "done":
                done_pickings += 1
        self.assertEqual(done_pickings, 0)

    def test_02_partial_deliveries(self):
        order = self._create_order(
            "delivery",
            [{"product_id": self.product.id, "product_uom_qty": 5.0}],
        )
        order.action_confirm()
        self.assertEqual(order.order_line.qty_to_invoice, 0.0)
        with self.assertRaises(UserError):
            order._create_invoices()
        backorder = self._deliver(order.picking_ids, 2.0)
        first_invoice = order._create_invoices()
        first_invoice.action_post()
        self.assertEqual(first_invoice.invoice_line_ids.quantity, 2.0)
        self.assertEqual(first_invoice.amount_untaxed, 40.0)
        self._deliver(backorder, 3.0)
        second_invoice = order._create_invoices()
        second_invoice.action_post()
        self.assertEqual(second_invoice.invoice_line_ids.quantity, 3.0)
        self.assertEqual(second_invoice.amount_untaxed, 60.0)
        self.assertEqual(len(order.invoice_ids), 2)
        self.assertEqual(order.order_line.qty_invoiced, 5.0)

    def test_03_product_policy_mode(self):
        order = self._create_order(
            "product",
            [
                {"product_id": self.product.id, "product_uom_qty": 2.0},
                {"product_id": self.product_delivery.id, "product_uom_qty": 3.0},
            ],
        )
        order.action_confirm()
        invoice = order._create_invoices()
        quantities = {}
        for line in invoice.invoice_line_ids:
            quantities[line.product_id] = line.quantity
        self.assertEqual(quantities[self.product], 2.0)
        self.assertNotIn(self.product_delivery, quantities)

    def test_04_order_policy_isolation(self):
        ordered = self._create_order(
            "order",
            [{"product_id": self.product.id, "product_uom_qty": 5.0}],
        )
        delivered = self._create_order(
            "delivery",
            [{"product_id": self.product.id, "product_uom_qty": 5.0}],
        )
        ordered.action_confirm()
        delivered.action_confirm()
        self.assertEqual(ordered.order_line.qty_to_invoice, 5.0)
        self.assertEqual(ordered.order_line.untaxed_amount_to_invoice, 100.0)
        self.assertEqual(delivered.order_line.qty_to_invoice, 0.0)
        self.assertEqual(delivered.order_line.untaxed_amount_to_invoice, 0.0)
        self.product.invalidate_recordset()
        self.assertEqual(self.product.invoice_policy, "order")
        ordered.invoice_policy = "delivery"
        self.assertEqual(ordered.order_line.invoice_policy, "delivery")
        self.assertEqual(ordered.order_line.qty_to_invoice, 0.0)

    def test_05_service_and_section(self):
        order = self._create_order(
            "delivery",
            [
                {"display_type": "line_section", "name": "Section"},
                {"product_id": self.service.id, "product_uom_qty": 2.0},
            ],
        )
        order.action_confirm()
        section = self.env["sale.order.line"]
        service_line = self.env["sale.order.line"]
        for line in order.order_line:
            if line.display_type:
                section = line
            if line.product_id == self.service:
                service_line = line
        self.assertEqual(section.qty_to_invoice, 0.0)
        self.assertEqual(section.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(service_line.invoice_policy, "order")
        self.assertEqual(service_line.qty_to_invoice, 2.0)
        self.assertEqual(service_line.untaxed_amount_to_invoice, 40.0)

    def test_06_combo_delivered_invoice(self):
        order = self._create_order(
            "delivery",
            [
                {
                    "product_id": self.product_combo.id,
                    "product_uom_qty": 3.0,
                    "price_unit": 0.0,
                }
            ],
        )
        header = order.order_line
        component_commands = []
        for combo in self.combo_a + self.combo_b:
            component_commands.append(
                Command.create(
                    {
                        "product_id": combo.combo_item_ids.product_id.id,
                        "product_uom_qty": 3.0,
                        "combo_item_id": combo.combo_item_ids.id,
                        "linked_line_id": header.id,
                    }
                )
            )
        order.order_line = component_commands
        order.action_confirm()
        with self.assertRaises(UserError):
            order._create_invoices()
        picking = order.picking_ids
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()
        invoice = order._create_invoices()
        invoice.action_post()
        self.assertEqual(len(order.invoice_ids), 1)
        invoiced_qty = 0.0
        for line in invoice.invoice_line_ids:
            invoiced_qty += line.quantity
        self.assertEqual(invoiced_qty, 6.0)
        self.assertEqual(invoice.amount_untaxed, order.amount_untaxed)
        invoiced_products = []
        for line in invoice.invoice_line_ids:
            self.assertNotIn(line.product_id, invoiced_products)
            invoiced_products.append(line.product_id)
        self.assertEqual(self.product.invoice_policy, "order")

    def test_07_full_payment_invoice(self):
        order = self._create_order(
            "delivery",
            [{"product_id": self.product.id, "product_uom_qty": 2.0}],
        )
        order.action_confirm()
        self.assertEqual(order.invoice_policy, "delivery")
        order._force_lines_to_invoice_policy_order()
        self.assertEqual(order.invoice_policy, "order")
        self.assertEqual(order.order_line.qty_to_invoice, 2.0)

        self.env.company.sudo().sale_automatic_invoice = True
        transaction = (
            self.env["payment.transaction"]
            .sudo()
            .create(
                {
                    "provider_id": self.provider.id,
                    "payment_method_id": self.payment_method.id,
                    "amount": order.amount_total,
                    "currency_id": order.currency_id.id,
                    "partner_id": order.partner_id.id,
                    "reference": f"TA43378-{order.id}",
                    "sale_order_ids": [Command.set(order.ids)],
                }
            )
        )
        transaction.with_context(payment_safe_write=True)._set_done()
        transaction.with_context(payment_safe_write=True)._invoice_sale_orders()
        self.assertEqual(order.invoice_policy, "order")
        self.assertEqual(len(order.invoice_ids), 1)
        order.invoice_ids.action_post()
        self.assertEqual(order.invoice_ids.state, "posted")
        self.assertEqual(order.order_line.qty_invoiced, 2.0)
        done_pickings = 0
        for picking in order.picking_ids:
            if picking.state == "done":
                done_pickings += 1
        self.assertEqual(done_pickings, 0)

    def test_08_multicompany_defaults_and_access(self):
        company_b = self.env["res.company"].sudo().create({"name": "Invoice policy B"})
        self.env.user.sudo().company_ids = [Command.link(company_b.id)]
        self.company.sudo().sale_default_invoice_policy = "order"
        company_b.sudo().sale_default_invoice_policy = "delivery"
        salesman = new_test_user(
            self.env(su=True),
            login="invoice_policy_salesman",
            groups="sales_team.group_sale_salesman,stock.group_stock_user",
            company_id=self.company.id,
            company_ids=[Command.set((self.company | company_b).ids)],
        )
        restricted = new_test_user(
            self.env(su=True),
            login="invoice_policy_restricted",
            groups="sales_team.group_sale_salesman",
            company_id=self.company.id,
            company_ids=[Command.set(self.company.ids)],
        )
        order_a = (
            self.env["sale.order"]
            .with_user(salesman)
            .with_context(allowed_company_ids=[self.company.id])
            .create(
                {
                    "partner_id": self.partner.id,
                    "company_id": self.company.id,
                    "user_id": salesman.id,
                }
            )
        )
        order_b = (
            self.env["sale.order"]
            .with_user(salesman)
            .with_context(allowed_company_ids=[company_b.id])
            .create(
                {
                    "partner_id": self.partner.id,
                    "company_id": company_b.id,
                    "user_id": salesman.id,
                }
            )
        )
        self.assertEqual(order_a.invoice_policy, "order")
        self.assertEqual(order_b.invoice_policy, "delivery")
        with self.assertRaises(AccessError):
            order_b.with_user(restricted).read(["invoice_policy"])

    def test_09_company_default_setting(self):
        settings = self.env["res.config.settings"].sudo().create({})
        settings.sale_default_invoice_policy = "delivery"
        settings.execute()
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertEqual(order.invoice_policy, "delivery")
        settings.sale_default_invoice_policy = "order"
        settings.execute()
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertEqual(order.invoice_policy, "order")

    def test_10_search_effective_policy(self):
        ordered = self._create_order(
            "order",
            [{"product_id": self.product_ordered_price.id, "product_uom_qty": 1.0}],
        )
        delivered = self._create_order(
            "delivery",
            [{"product_id": self.product.id, "product_uom_qty": 1.0}],
        )
        service_order = self._create_order(
            "delivery",
            [{"product_id": self.service.id, "product_uom_qty": 1.0}],
        )
        found = self.env["sale.order.line"].search(
            [
                ("id", "in", (ordered | delivered | service_order).order_line.ids),
                ("invoice_policy", "=", "order"),
            ]
        )
        self.assertIn(ordered.order_line, found)
        self.assertIn(service_order.order_line, found)
        self.assertNotIn(delivered.order_line, found)
