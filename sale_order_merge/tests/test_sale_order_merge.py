# Copyright 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderMerge(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal_sale = cls.env["account.journal"].create(
            {
                "company_id": cls.env.company.id,
                "name": "Test journal for sale",
                "type": "sale",
                "code": "TSALE",
            }
        )
        cls.env.ref("product.product_product_24").write(
            {
                "list_price": 2,
            }
        )
        cls.env.ref("product.product_product_25").write(
            {
                "list_price": 3,
            }
        )

    def create_sale_orders(self):
        order1 = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_24").id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        order2 = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_24").id,
                            "product_uom_qty": 1,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_25").id,
                            "product_uom_qty": 1,
                        }
                    ),
                ],
            }
        )
        return order1, order2

    def create_wizard_merge(self, order_id, order_ids):
        return (
            self.env["sale.order.merge"]
            .with_context(
                **{
                    "default_to_merge_ids": [Command.set(order_ids)],
                    "default_order_id": order_id.id,
                }
            )
            .create({})
        )

    def test_action_button_merge(self):
        order1, order2 = self.create_sale_orders()
        order_id = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_24").id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        result = order_id.action_button_merge()
        wizard_result = self.env["sale.order.merge"].browse(result["res_id"])
        merge_ids = wizard_result.to_merge_ids.ids
        self.assertIn(order1.id, merge_ids)
        self.assertIn(order2.id, merge_ids)
        self.assertEqual(order_id.id, wizard_result.order_id.id)
        wizard_id = self.create_wizard_merge(order_id, [order1.id, order2.id])
        with Form(wizard_id) as form_merge:
            self.assertEqual(len(form_merge.to_merge_ids), 2)
            self.assertIn(order1, form_merge.to_merge_ids)
            wizard_id.merge()

        line_ids = order_id.order_line
        self.assertEqual(order_id.state, "draft")
        self.assertEqual(len(line_ids), 4)

        order3, order4 = self.create_sale_orders()
        order3.action_confirm()
        order3._create_invoices()
        wizard3_id = self.create_wizard_merge(order_id, [order3.id, order4.id])
        self.assertTrue(wizard3_id.message_alert)
        order_id.action_confirm()
        with Form(wizard3_id) as form_merge:
            self.assertEqual(len(form_merge.to_merge_ids), 2)
            self.assertIn(order3, form_merge.to_merge_ids)
            wizard3_id.merge()
        self.assertTrue(wizard3_id.message_alert)
        self.assertEqual(order_id.state, "sale")
        self.assertEqual(order3.state, "cancel")
        self.assertEqual(order4.state, "cancel")
        self.assertEqual(len(order3.picking_ids), 0)
        self.assertEqual(len(order4.picking_ids), 0)
        self.assertEqual(len(order_id.invoice_ids), 1)

    def test_validate_selected_message_error(self):
        order1, order2 = self.create_sale_orders()
        order_invalid = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_3").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_24").id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        orders = order_invalid | order1 | order2
        with self.assertRaises(ValidationError) as exPartner:
            orders.action_button_merge()
        msg_partner = str(exPartner.exception)
        self.assertIn("Partner - Orders", msg_partner)
        self.assertIn(self.env.ref("base.res_partner_3").name, msg_partner)
        order_invalid.write(
            {"partner_shipping_id": self.env.ref("base.res_partner_3").id}
        )
        with self.assertRaises(ValidationError) as exDelivery:
            orders.action_button_merge()
        msg_delivery = str(exDelivery.exception)
        self.assertIn("Delivery address - Orders", msg_delivery)
        self.assertIn(self.env.ref("base.res_partner_3").name, msg_delivery)

        company = self.env["res.company"].create(
            {
                "name": "Test Company",
            }
        )
        order_invalid.write({"company_id": company.id})
        with self.assertRaises(ValidationError) as exCompany:
            orders.action_button_merge()
        msg_company = str(exCompany.exception)
        self.assertIn("Company - Orders", msg_company)
        self.assertIn(company.name, msg_company)

        warehouse_id = self.env["stock.warehouse"].create(
            {"name": "Test Warehouse", "code": "TESTW", "company_id": company.id}
        )
        order_invalid.write({"warehouse_id": warehouse_id.id})
        with self.assertRaises(ValidationError) as exWarehouse:
            orders.action_button_merge()
        msg_warehouse = str(exWarehouse.exception)
        self.assertIn("Warehouse - Orders", msg_warehouse)
        self.assertIn(warehouse_id.name, msg_warehouse)

        currency_eur = self.env.ref("base.EUR")
        currency_eur.active = True
        order_invalid.write({"currency_id": currency_eur.id})
        with self.assertRaises(ValidationError) as exCurrency:
            orders.action_button_merge()
        msg_currency = str(exCurrency.exception)
        self.assertIn("Currency - Orders", msg_currency)
        self.assertIn(self.env.ref("base.res_partner_3").name, msg_currency)

        order_confirm = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_27").id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        conf = self.env["res.config.settings"].create({"merge_order_confirm": False})
        conf.execute()
        order_confirm.action_confirm()
        with self.assertRaises(ValidationError) as exState:
            (orders | order_confirm).action_button_merge()
        msg_state = str(exState.exception)
        self.assertIn("State - Orders", msg_state)
        self.assertIn("Sale", msg_state)

    def test_merge_order_by_states(self):
        conf = self.env["res.config.settings"].create({"merge_order_confirm": True})
        conf.execute()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_10").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_5").id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        result = order._merge_order_by_states()
        self.assertIn("sale", result)


class TestSaleOrderMergeConfirmed(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(
            "sale_order_merge.merge_order_confirm", True
        )
        cls.customer = cls.env["res.partner"].create({"name": "Merge customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Merge product",
                "type": "consu",
                "invoice_policy": "order",
                "list_price": 10,
            }
        )

    def _create_order(self, qty=1):
        return self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": qty}
                    )
                ],
            }
        )

    def _merge(self, target, orders):
        wizard = self.env["sale.order.merge"].create(
            {
                "order_id": target.id,
                "to_merge_ids": [Command.set((target | orders).ids)],
            }
        )
        return wizard.merge()

    def test_merge_ok_needs_another_order(self):
        order = self._create_order()
        self.assertFalse(order.merge_ok)
        self.assertFalse(order.merge_with_ids)
        other = self._create_order()
        order.invalidate_recordset(["merge_ok", "merge_with_ids"])
        self.assertTrue(order.merge_ok)
        self.assertEqual(order.merge_with_ids, other)

    def test_merge_ok_in_form(self):
        order = self._create_order()
        other = self._create_order()
        with Form(order) as order_form:
            with order_form.order_line.new() as line_form:
                line_form.product_id = self.product
            self.assertTrue(order_form.merge_ok)
        self.assertEqual(order.merge_with_ids, other)

    def test_merge_sent_quotation(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_merge.merge_order_confirm", False
        )
        target = self._create_order()
        other = self._create_order(qty=2)
        other.action_quotation_sent()
        self.assertEqual(target.merge_with_ids, other)
        target.action_quotation_sent()
        target.invalidate_recordset(["merge_ok", "merge_with_ids"])
        self.assertTrue(target.merge_ok)
        self._merge(target, other)
        self.assertEqual(other.state, "cancel")
        self.assertEqual(target.state, "sent")
        self.assertEqual(sum(target.order_line.mapped("product_uom_qty")), 3)

    def test_search_merge_with_ids_operator(self):
        order = self._create_order()
        other = self._create_order()
        found = self.env["sale.order"].search([("merge_with_ids", "=", order.id)])
        self.assertEqual(found, other)
        with self.assertRaises(NotImplementedError):
            self.env["sale.order"].search([("merge_with_ids", "!=", order.id)])

    def test_merge_messages(self):
        target = self._create_order()
        other = self._create_order()
        action = self._merge(target, other)
        self.assertEqual(action["type"], "ir.actions.act_window_close")
        self.assertIn(target.name, other.message_ids[0].body)
        target_body = target.message_ids[0].body
        self.assertIn(other.name, target_body)
        self.assertNotIn(target.name, target_body)

    def test_merge_pickings(self):
        target = self._create_order(qty=1)
        other = self._create_order(qty=2)
        # Confirmed together, both pickings share their scheduled date, so the
        # newest one, of the other order, comes first in the default order
        (target | other).action_confirm()
        other_picking = other.picking_ids
        target_picking = target.picking_ids
        # Start from an empty cache, as a new request does
        self.env.invalidate_all()
        self._merge(target, other)
        self.assertFalse(other_picking.exists())
        picking = target.picking_ids
        self.assertEqual(picking, target_picking)
        self.assertEqual(sum(picking.move_ids.mapped("product_uom_qty")), 3)
        self.assertEqual(picking.move_ids.picking_id, picking)

    def test_merge_draft_invoices(self):
        target = self._create_order(qty=1)
        other = self._create_order(qty=2)
        (target | other).action_confirm()
        target_invoice = target._create_invoices()
        other_invoice = other._create_invoices()
        self._merge(target, other)
        self.assertFalse(other_invoice.exists())
        self.assertEqual(target.invoice_ids, target_invoice)
        self.assertEqual(sum(target_invoice.invoice_line_ids.mapped("quantity")), 3)
        self.assertEqual(target_invoice.amount_untaxed, 30)
        self.assertEqual(target_invoice.amount_total, target.amount_total)

    def test_merge_locked_order(self):
        target = self._create_order()
        other = self._create_order()
        (target | other).action_confirm()
        other.action_lock()
        with self.assertRaises(UserError):
            self._merge(target, other)
        self.assertEqual(other.state, "sale")
