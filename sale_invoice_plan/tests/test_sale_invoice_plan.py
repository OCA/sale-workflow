# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from collections import OrderedDict

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from odoo.addons.sale.tests import common


class TestSaleInvoicePlan(common.TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super(TestSaleInvoicePlan, cls).setUpClass()
        context_no_mail = {
            "no_reset_password": True,
            "mail_create_nosubscribe": True,
            "mail_create_nolog": True,
        }

        # Create base account to simulate a chart of account
        user_type_payable = cls.env.ref("account.data_account_type_payable")
        cls.account_payable = cls.env["account.account"].create(
            {
                "code": "NC1110",
                "name": "Test Payable Account",
                "user_type_id": user_type_payable.id,
                "reconcile": True,
            }
        )
        user_type_receivable = cls.env.ref("account.data_account_type_receivable")
        cls.account_receivable = cls.env["account.account"].create(
            {
                "code": "NC1111",
                "name": "Test Receivable Account",
                "user_type_id": user_type_receivable.id,
                "reconcile": True,
            }
        )

        Partner = cls.env["res.partner"].with_context(context_no_mail)
        cls.partner_customer_usd = Partner.create(
            {
                "name": "Customer from the North",
                "email": "customer.usd@north.com",
                "property_account_payable_id": cls.account_payable.id,
                "property_account_receivable_id": cls.account_receivable.id,
            }
        )

        cls.sale_journal0 = cls.env["account.journal"].create(
            {
                "name": "Sale Journal",
                "type": "sale",
                "code": "SJT0",
            }
        )

        cls.setUpClassicProducts()

        sale_obj = cls.env["sale.order"]
        # Create an SO for Service
        cls.so_service = sale_obj.with_user(
            cls.company_data["default_user_salesman"]
        ).create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "partner_invoice_id": cls.partner_customer_usd.id,
                "partner_shipping_id": cls.partner_customer_usd.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_order.name,
                            "product_id": cls.product_order.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_order.uom_id.id,
                            "price_unit": cls.product_order.list_price,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        # Create an SO for product delivery
        cls.so_product = sale_obj.with_user(
            cls.company_data["default_user_salesman"]
        ).create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "partner_invoice_id": cls.partner_customer_usd.id,
                "partner_shipping_id": cls.partner_customer_usd.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_deliver.name,
                            "product_id": cls.product_deliver.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product_deliver.uom_id.id,
                            "price_unit": cls.product_deliver.list_price,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

    @classmethod
    def setUpClassicProducts(cls):
        # Create an expense journal
        user_type_income = cls.env.ref("account.data_account_type_direct_costs")
        cls.account_income_product = cls.env["account.account"].create(
            {
                "code": "INCOME_PROD111",
                "name": "Icome - Test Account",
                "user_type_id": user_type_income.id,
            }
        )
        # Create category
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Product Category with Income account",
                "property_account_income_categ_id": cls.account_income_product.id,
            }
        )
        # Products
        uom_unit = cls.env.ref("uom.product_uom_unit")
        uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "Zed+ Antivirus",
                "standard_price": 235.0,
                "list_price": 280.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "invoice_policy": "order",
                "expense_policy": "no",
                "default_code": "PROD_ORDER",
                "service_type": "manual",
                "taxes_id": False,
                "categ_id": cls.product_category.id,
            }
        )
        cls.service_deliver = cls.env["product.product"].create(
            {
                "name": "Cost-plus Contract",
                "standard_price": 200.0,
                "list_price": 180.0,
                "type": "service",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "invoice_policy": "delivery",
                "expense_policy": "no",
                "default_code": "SERV_DEL",
                "service_type": "manual",
                "taxes_id": False,
                "categ_id": cls.product_category.id,
            }
        )
        cls.service_order = cls.env["product.product"].create(
            {
                "name": "Prepaid Consulting",
                "standard_price": 40.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "invoice_policy": "order",
                "expense_policy": "no",
                "default_code": "PRE-PAID",
                "service_type": "manual",
                "taxes_id": False,
                "categ_id": cls.product_category.id,
            }
        )
        cls.product_deliver = cls.env["product.product"].create(
            {
                "name": "Switch, 24 ports",
                "standard_price": 55.0,
                "list_price": 70.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "invoice_policy": "delivery",
                "expense_policy": "no",
                "default_code": "PROD_DEL",
                "service_type": "manual",
                "taxes_id": False,
                "categ_id": cls.product_category.id,
            }
        )

        cls.product_map = OrderedDict(
            [
                ("prod_order", cls.product_order),
                ("serv_del", cls.service_deliver),
                ("serv_order", cls.service_order),
                ("prod_del", cls.product_deliver),
            ]
        )

    def test_00_invoice_plan(self):
        # To create next invoice from SO
        ctx = {
            "active_id": self.so_service.id,
            "active_ids": [self.so_service.id],
            "all_remain_invoices": False,
        }
        f = Form(self.env["sale.create.invoice.plan"])
        try:  # UserError if no installment
            plan = f.save()
        except ValidationError:
            pass
        # Create Invoice Plan 3 installment
        num_installment = 3
        f.num_installment = num_installment
        # Test 3 types of interval
        for interval_type in ["month", "year", "day"]:
            f.interval_type = interval_type
            plan = f.save()
            # SO confirmed without invoice plan being created
            if not self.so_service.invoice_plan_ids:
                with self.assertRaises(UserError):
                    self.so_service.action_confirm()
            # Create Invocie Plan Installment
            plan.with_context(ctx).sale_create_invoice_plan()
            self.assertEqual(
                len(self.so_service.invoice_plan_ids),
                num_installment,
                "Wrong number of installment created",
            )
        # Confirm the SO
        self.so_service.action_confirm()
        # Create one invoice
        make_wizard = self.env["sale.make.planned.invoice"].create({})
        make_wizard.with_context(ctx).create_invoices_by_plan()
        invoices = self.so_service.invoice_ids
        self.assertEqual(len(invoices), 1, "Only 1 invoice should be created")

    def test_01_invoice_plan(self):
        # To create all remaining invoice from SO
        ctx = {
            "active_id": self.so_service.id,
            "active_ids": [self.so_service.id],
            "advance_payment_method": "delivered",
            "all_remain_invoices": True,
        }
        f = Form(self.env["sale.create.invoice.plan"])
        # Create Invoice Plan 3 installment
        num_installment = 3
        # Test 3 types of interval
        for interval_type in ["month", "year", "day"]:
            f.interval_type = interval_type
            f.num_installment = num_installment
            plan = f.save()
            plan.with_context(ctx).sale_create_invoice_plan()
        # Confirm the SO
        self.so_service.action_confirm()
        # Create all invoices
        make_wizard = self.env["sale.make.planned.invoice"].create({})
        make_wizard.with_context(ctx).create_invoices_by_plan()
        # Valid number of invoices
        invoices = self.so_service.invoice_ids
        self.assertEqual(
            len(invoices), num_installment, "Wrong number of invoice created"
        )
        # Valid total quantity of invoices
        quantity = sum(invoices.mapped("invoice_line_ids").mapped("quantity"))
        self.assertEqual(quantity, 1, "Wrong number of total invoice quantity")

    def test_02_invoice_plan_with_advance(self):
        # To create all remaining invoice from SO
        ctx = {
            "active_id": self.so_service.id,
            "active_ids": [self.so_service.id],
            "all_remain_invoices": True,
        }
        # Create Invoice Plan 3 installment with Advance
        num_installment = 3
        f = Form(self.env["sale.create.invoice.plan"])
        f.num_installment = num_installment
        f.advance = True  # Advance
        plan = f.save()
        plan.with_context(ctx).sale_create_invoice_plan()
        self.assertEqual(
            len(self.so_service.invoice_plan_ids),
            num_installment + 1,
            "Wrong number of installment created",
        )
        # If advance percent is not filled, show error
        with self.assertRaises(ValidationError):
            self.so_service.action_confirm()
        advance_line = self.so_service.invoice_plan_ids.filtered(
            lambda l: l.invoice_type == "advance"
        )
        self.assertEqual(len(advance_line), 1, "No one advance line")
        # Add 10% to advance
        advance_line.percent = 10
        # Can confirm the SO after advance is filled
        self.so_service.action_confirm()
        # Create all invoice plan
        wizard = self.env["sale.make.planned.invoice"].create({})
        wizard.with_context(ctx).create_invoices_by_plan()
        # Valid number of invoices, including advance
        invoices = self.so_service.invoice_ids
        self.assertEqual(
            len(invoices), num_installment + 1, "Wrong number of invoice created"
        )
        # Valid total quantity of invoices (exclude Advance line)
        quantity = sum(
            invoices.mapped("invoice_line_ids")
            .filtered(lambda l: l.product_id == self.product_order)
            .mapped("quantity")
        )
        self.assertEqual(quantity, 1, "Wrong number of total invoice quantity")

    def test_03_unlink_invoice_plan(self):
        ctx = {"active_id": self.so_service.id, "active_ids": [self.so_service.id]}
        f = Form(self.env["sale.create.invoice.plan"])
        # Create Invoice Plan 3 installment
        num_installment = 3
        f.num_installment = num_installment
        plan = f.save()
        plan.with_context(ctx).sale_create_invoice_plan()
        # Remove it
        self.so_service.remove_invoice_plan()
        self.assertFalse(self.so_service.invoice_plan_ids)

    def test_04_invoice_plan_over_delivered_quantity(self):
        # To create all remaining invoice from SO
        ctx = {
            "active_id": self.so_product.id,
            "active_ids": [self.so_product.id],
            "all_remain_invoices": True,
        }
        # Create Invoice Plan 2 installment
        num_installment = 2
        f = Form(self.env["sale.create.invoice.plan"])
        f.num_installment = num_installment
        plan = f.save()
        plan.with_context(ctx).sale_create_invoice_plan()
        self.so_product.action_confirm()
        # Delivery product 3 qty out of 10
        self.assertEqual(len(self.so_product.picking_ids), 1)
        pick = self.so_product.picking_ids[0]
        pick.move_ids_without_package.write({"quantity_done": 3.0})
        pick._action_done()
        # Create invoice by plan
        wizard = self.env["sale.make.planned.invoice"].create({})
        with self.assertRaises(ValidationError) as e:
            wizard.with_context(ctx).create_invoices_by_plan()
        self.assertIn(
            "Plan quantity: 5.0, exceed invoiceable quantity: 3.0", e.exception.name
        )
        # Deliver all the rest and create invoice plan again
        pick = self.so_product.picking_ids.filtered(lambda l: l.state != "done")
        pick.mapped("move_ids_without_package").write({"quantity_done": 7.0})
        pick._action_done()
        wizard = self.env["sale.make.planned.invoice"].create({})
        wizard.with_context(ctx).create_invoices_by_plan()
        # Valid total quantity of invoice = 10 units
        invoices = self.so_product.invoice_ids
        quantity = sum(invoices.mapped("invoice_line_ids").mapped("quantity"))
        self.assertEqual(quantity, 10, "Wrong number of total invoice quantity")
