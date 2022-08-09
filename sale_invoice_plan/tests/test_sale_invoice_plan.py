# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged

from odoo.addons.sale.tests import common

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
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

        Partner = cls.env["res.partner"].with_context(**context_no_mail)
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
        except ValidationError as e:
            _logger.info(_("No installment raises following error : %s"), e.args[0])
        # Create Invoice Plan 3 installment
        num_installment = 5
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
            plan.with_context(**ctx).sale_create_invoice_plan()
            self.assertEqual(
                len(self.so_service.invoice_plan_ids),
                num_installment,
                "Wrong number of installment created",
            )
        # Change plan, so that the 1st installment is 1000 and 5th is 3000
        self.assertEqual(len(self.so_service.invoice_plan_ids), 5)
        self.so_service.invoice_plan_ids[0].amount = 280.0
        self.so_service.invoice_plan_ids[4].amount = 840.0
        # Confirm the SO
        self.so_service.action_confirm()
        # Create one invoice
        make_wizard = self.env["sale.make.planned.invoice"].create({})
        make_wizard.with_context(**ctx).create_invoices_by_plan()
        self.assertEqual(
            self.so_service.amount_total,
            sum(self.so_service.invoice_ids.mapped("amount_total")),
        )
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
            plan.with_context(**ctx).sale_create_invoice_plan()
        # Confirm the SO
        self.so_service.action_confirm()
        # Create all invoices
        make_wizard = self.env["sale.make.planned.invoice"].create({})
        make_wizard.with_context(**ctx).create_invoices_by_plan()
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
        plan.with_context(**ctx).sale_create_invoice_plan()
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
        wizard.with_context(**ctx).create_invoices_by_plan()
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
        plan.with_context(**ctx).sale_create_invoice_plan()
        # Remove it
        self.so_service.remove_invoice_plan()
        self.assertFalse(self.so_service.invoice_plan_ids)

    def test_invoice_plan_so_edit(self):
        """Case when some installment already invoiced,
        but then, the SO line added. Test to ensure that
        the invoiced amount of the done installment is fixed"""
        ctx = {
            "active_id": self.so_service.id,
            "active_ids": [self.so_service.id],
            "all_remain_invoices": False,
        }
        first_order_line = fields.first(self.so_service.order_line)
        first_order_line.product_uom_qty = 10
        f = Form(self.env["sale.create.invoice.plan"])
        # Create Invoice Plan 5 installment
        num_installment = 5
        f.num_installment = num_installment
        plan = f.save()
        plan.with_context(**ctx).sale_create_invoice_plan()
        # Change plan, so that the 1st installment is 280 and 5th is 840
        self.assertEqual(len(self.so_service.invoice_plan_ids), 5)
        first_install = self.so_service.invoice_plan_ids[0]
        first_install.amount = 280.0
        self.so_service.invoice_plan_ids[4].amount = 840.0
        self.so_service.action_confirm()
        self.assertEqual(self.so_service.state, "sale")
        sale_create = self.env["sale.make.planned.invoice"].create({})
        # Create only the 1st invoice, amount should be 280, and percent is 10
        sale_create.with_context(**ctx).create_invoices_by_plan()
        self.assertEqual(first_install.amount, 280.0)
        self.assertEqual(first_install.percent, 10)
        # Add new SO line with amount = 280, check that only percent is changed
        self.so_service.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "SO-Product-NEW",
                            "product_id": self.product_order.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_order.uom_id.id,
                            "price_unit": 280.0,
                        },
                    )
                ],
            }
        )
        # Overall amount changed to 3080, install amount not changed, only percent changed.
        self.assertEqual(self.so_service.amount_total, 3080.0)
        self.so_service.invoice_plan_ids._compute_amount()
        self.assertEqual(first_install.amount, 280.0)
        self.assertEqual(first_install.percent, 9.090909)
