# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Pierre Faniel - Niboo SPRL (<https://www.niboo.be/>)
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from freezegun import freeze_time

import odoo.tests.common as common
from odoo import fields
from odoo.tests import Form


class TestSaleOrderType(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderType, self).setUp()
        self.sale_type_model = self.env["sale.order.type"]
        self.sale_order_model = self.env["sale.order"]
        self.invoice_model = self.env["account.move"].with_context(
            default_type="out_invoice"
        )
        self.partner = self.env.ref("base.res_partner_1")
        self.partner_child_1 = self.env["res.partner"].create(
            {"name": "Test child", "parent_id": self.partner.id, "sale_type": False}
        )
        self.sequence = self.env["ir.sequence"].create(
            {
                "name": "Test Sales Order",
                "code": "sale.order",
                "prefix": "TSO",
                "padding": 3,
            }
        )
        self.sequence_quot = self.env["ir.sequence"].create(
            {
                "name": "Test Quotation Update",
                "code": "sale.order",
                "prefix": "TQU",
                "padding": 3,
            }
        )
        self.journal = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        self.default_sale_type_id = self.env["sale.order.type"].search([], limit=1)
        self.default_sale_type_id.sequence_id = False
        self.product = self.env["product.product"].create(
            {"type": "service", "invoice_policy": "order", "name": "Test product"}
        )
        self.immediate_payment = self.env.ref("account.account_payment_term_immediate")
        self.sale_pricelist = self.env.ref("product.list0")
        self.sale_type = self.sale_type_model.create(
            {
                "name": "Test Sale Order Type",
                "sequence_id": self.sequence.id,
                "journal_id": self.journal.id,
                "payment_term_id": self.immediate_payment.id,
                "pricelist_id": self.sale_pricelist.id,
                "quotation_validity_days": 10,
            }
        )
        self.sale_type_quot = self.sale_type_model.create(
            {
                "name": "Test Quotation Type",
                "sequence_id": self.sequence_quot.id,
                "journal_id": self.journal.id,
                "payment_term_id": self.immediate_payment.id,
                "pricelist_id": self.sale_pricelist.id,
            }
        )
        self.sale_type_sequence_default = self.sale_type_quot.copy(
            {
                "name": "Test Sequence default",
                "sequence_id": self.env["sale.order"]
                .with_context(force_company=self.env.company.id)
                ._default_sequence_id()
                .id,
            }
        )
        self.partner.sale_type = self.sale_type

    def create_sale_order(self, partner=False):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = partner or self.partner
        with sale_form.order_line.new() as order_line:
            order_line.product_id = self.product
            order_line.product_uom_qty = 1.0
        return sale_form.save()

    def create_invoice(self, partner=False, sale_type=False):
        inv_form = Form(
            self.env["account.move"].with_context({"default_type": "out_invoice"})
        )
        inv_form.partner_id = partner or self.partner
        inv_form.sale_type_id = sale_type or self.sale_type
        with inv_form.invoice_line_ids.new() as inv_line:
            inv_line.product_id = self.product
            inv_line.quantity = 1.0
        return inv_form.save()

    def test_sale_order_flow(self):
        sale_type = self.sale_type
        order = self.create_sale_order()
        self.assertEqual(order.type_id, sale_type)
        order.onchange_type_id()
        self.assertEqual(order.payment_term_id, sale_type.payment_term_id)
        self.assertEqual(order.pricelist_id, sale_type.pricelist_id)
        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(invoice.sale_type_id, sale_type)
        self.assertEqual(invoice.journal_id, sale_type.journal_id)

    def test_sale_order_change_partner(self):
        order = self.create_sale_order()
        self.assertEqual(order.type_id, self.sale_type)
        order = self.create_sale_order(partner=self.partner_child_1)
        self.assertEqual(order.type_id, self.sale_type)

    def test_invoice_onchange_type(self):
        sale_type = self.sale_type
        invoice = self.create_invoice()
        invoice.onchange_sale_type_id()
        self.assertEqual(invoice.invoice_payment_term_id, sale_type.payment_term_id)
        self.assertEqual(invoice.journal_id, sale_type.journal_id)

    def test_invoice_change_partner(self):
        invoice = self.create_invoice()
        self.assertEqual(invoice.sale_type_id, self.sale_type)
        invoice = self.create_invoice(partner=self.partner_child_1)
        self.assertEqual(invoice.sale_type_id, self.sale_type)

    def test_invoice_without_partner(self):
        invoice = self.invoice_model.new()
        self.assertEqual(invoice.sale_type_id, self.default_sale_type_id)

    def test_sale_order_in_draft_state_update_name(self):
        order = self.create_sale_order()
        order.onchange_partner_id()
        order.onchange_type_id()
        self.assertEqual(order.type_id, self.sale_type)
        self.assertEqual(order.state, "draft")
        self.assertTrue(order.name.startswith("TSO"))
        # change order type on sale order
        order.type_id = self.sale_type_quot
        order.onchange_type_id()
        self.assertEqual(order.type_id, self.sale_type_quot)
        self.assertTrue(order.name.startswith("TQU"))

    def test_sale_order_in_sent_state_update_name(self):
        order = self.create_sale_order()
        order.onchange_partner_id()
        order.onchange_type_id()
        self.assertEqual(order.type_id, self.sale_type)
        self.assertEqual(order.state, "draft")
        self.assertTrue(order.name.startswith("TSO"))
        # send quotation
        order.action_quotation_sent()
        self.assertTrue(order.state == "sent", "Sale: state after sending is wrong")
        # change order type on sale order
        order.type_id = self.sale_type_quot
        order.onchange_type_id()
        self.assertEqual(order.type_id, self.sale_type_quot)
        self.assertTrue(order.name.startswith("TQU"))

    @freeze_time("2022-01-01")
    def test_sale_order_quotation_validity(self):
        order = self.create_sale_order()
        order.onchange_type_id()
        self.assertEqual(fields.Date.to_string(order.validity_date), "2022-01-11")

    def test_sequence_default(self):
        """When the previous type had no sequence the order gets the default one. The
        sequence change shouldn't be triggered, otherwise we'd get a different number
        from the same sequence"""
        self.partner.sale_type = self.default_sale_type_id
        order = self.create_sale_order()
        order.onchange_partner_id()
        name = order.name
        order.type_id = self.sale_type_sequence_default
        self.assertEqual(name, order.name, "The sequence shouldn't change!")

    def test_sale_order_copy_and_write(self):
        order = self.create_sale_order()
        self.assertEqual(order.name, "TSO001")
        # Copy this one
        new_order = order.copy()
        self.assertEqual(new_order.name, "TSO002")
        # Create new sequence and type
        sequence = self.env["ir.sequence"].create(
            {
                "name": "Test Sales Order Copy",
                "code": "sale.order",
                "prefix": "CP0",
                "padding": 1,
            }
        )
        sale_type = self.sale_type_model.create(
            {
                "name": "Test Sale Order Type Copy",
                "sequence_id": sequence.id,
                "journal_id": self.journal.id,
                "payment_term_id": self.immediate_payment.id,
                "pricelist_id": self.sale_pricelist.id,
            }
        )
        # Change sale type for copied order
        new_order.write({"type_id": sale_type.id})
        # See that name has changed
        self.assertEqual(new_order.name, "CP01")
        # Restore the original type and see
        # sequence increasing
        new_order.write({"type_id": self.sale_type.id})
        self.assertEqual(new_order.name, "TSO003")
        # Write again on the same order, and see nothing
        # is changing
        new_order.write({"type_id": self.sale_type.id})
        self.assertEqual(new_order.name, "TSO003")
        # Create a new type, with no sequence
        sale_type_no_sequence = self.sale_type_model.create(
            {
                "name": "Test Sale Order Type No Sequence",
                "journal_id": self.journal.id,
                "payment_term_id": self.immediate_payment.id,
                "pricelist_id": self.sale_pricelist.id,
            }
        )
        # Write again, and see that name remains the same
        new_order.write({"type_id": sale_type_no_sequence.id})
        self.assertEqual(new_order.name, "TSO003")
