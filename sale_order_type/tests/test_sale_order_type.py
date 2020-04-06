# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Pierre Faniel - Niboo SPRL (<https://www.niboo.be/>)
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestSaleOrderType(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderType, self).setUp()
        self.sale_type_model = self.env["sale.order.type"]
        self.sale_order_model = self.env["sale.order"]
        self.invoice_model = self.env["account.move"]
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
        self.journal = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        self.warehouse = self.env["stock.warehouse"].create(
            {"name": "Warehouse Test", "code": "WT"}
        )
        self.product = self.env["product.product"].create(
            {"type": "service", "invoice_policy": "order", "name": "Test product"}
        )
        self.immediate_payment = self.env.ref("account.account_payment_term_immediate")
        self.sale_pricelist = self.env.ref("product.list0")
        self.free_carrier = self.env.ref("account.incoterm_FCA")
        self.sale_type = self.sale_type_model.create(
            {
                "name": "Test Sale Order Type",
                "sequence_id": self.sequence.id,
                "journal_id": self.journal.id,
                "warehouse_id": self.warehouse.id,
                "picking_policy": "one",
                "payment_term_id": self.immediate_payment.id,
                "pricelist_id": self.sale_pricelist.id,
                "incoterm_id": self.free_carrier.id,
            }
        )
        self.partner.sale_type = self.sale_type

    def get_sale_order_vals(self):
        sale_line_dict = {
            "product_id": self.product.id,
            "name": self.product.name,
            "product_uom_qty": 1.0,
            "price_unit": self.product.lst_price,
        }
        return {"partner_id": self.partner.id, "order_line": [(0, 0, sale_line_dict)]}

    def test_sale_order_flow(self):
        sale_type = self.sale_type
        order = self.sale_order_model.create(self.get_sale_order_vals())
        self.assertEqual(order.type_id, sale_type)
        order.onchange_type_id()
        self.assertEqual(order.warehouse_id, sale_type.warehouse_id)
        self.assertEqual(order.picking_policy, sale_type.picking_policy)
        self.assertEqual(order.payment_term_id, sale_type.payment_term_id)
        self.assertEqual(order.pricelist_id, sale_type.pricelist_id)
        self.assertEqual(order.incoterm, sale_type.incoterm_id)
        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(invoice.sale_type_id, sale_type)
        self.assertEqual(invoice.journal_id, sale_type.journal_id)

    def test_sale_order_change_partner(self):
        order = self.sale_order_model.new({"partner_id": self.partner.id})
        self.assertEqual(order.type_id, self.sale_type)
        order = self.sale_order_model.new({"partner_id": self.partner_child_1.id})
        self.assertEqual(order.type_id, self.sale_type)

    def test_invoice_onchange_type(self):
        sale_type = self.sale_type
        invoice = self.invoice_model.new({"sale_type_id": sale_type.id})
        invoice.onchange_sale_type_id()
        self.assertEqual(invoice.invoice_payment_term_id, sale_type.payment_term_id)
        self.assertEqual(invoice.journal_id, sale_type.journal_id)

    def test_invoice_change_partner(self):
        invoice = self.invoice_model.new({"partner_id": self.partner.id})
        self.assertEqual(invoice.sale_type_id, self.sale_type)
        invoice = self.invoice_model.new({"partner_id": self.partner_child_1.id})
        self.assertEqual(invoice.sale_type_id, self.sale_type)
