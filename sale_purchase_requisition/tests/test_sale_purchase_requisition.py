# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests.common import Form, SavepointCase, new_test_user, users


class TestSalePurchaseRequisition(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.products = cls.env["product.product"].create(
            [
                {
                    "name": "Product A",
                    "default_code": "PA",
                    "lst_price": 100.0,
                    "standard_price": 100.0,
                },
                {
                    "name": "Product B",
                    "default_code": "PB",
                    "lst_price": 50.0,
                    "standard_price": 50.0,
                },
            ]
        )
        cls.salesperson = new_test_user(
            cls.env, "test_salesperson", groups="sales_team.group_sale_salesman"
        )
        cls.purchaseperson = new_test_user(
            cls.env, "test_purchaseperson", groups="purchase.group_purchase_user"
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "test customer",
            }
        )
        cls.sale_overseer = new_test_user(
            cls.env,
            "test_sale_overseer",
            groups="sales_team.group_sale_salesman_all_leads",
        )
        cls.full_overseer = new_test_user(
            cls.env,
            "test_full_overseer",
            groups="sales_team.group_sale_manager,purchase.group_purchase_manager",
        )

    @users("test_salesperson")
    def test_create_purchase_requisition(self):
        # User creates a sale order
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.products[0]
            line_form.product_uom_qty = 10
        so = so_form.save()
        # User creates the related purchase requisition
        action = so.action_create_purchase_requisition()
        self.assertFalse("res_id" in action)
        pr_form = Form(self.env[action["res_model"]].with_context(action["context"]))
        pr = pr_form.save()
        self.assertFalse(pr.user_id)
        self.assertEqual(pr.sale_user_id, so.user_id)
        self.assertRecordValues(
            pr.line_ids, [{"product_id": self.products[0].id, "product_qty": 10}]
        )
        # Make sure that user can still find and edit the PR
        action = so.action_create_purchase_requisition()
        self.assertEqual(action["res_model"], pr._name)
        pr = pr.with_context(action["context"])
        with Form(pr) as pr_form:
            self.assertEqual(pr_form.state, "draft")
            pr_form.user_id = self.env.user
        self.assertEqual(pr.user_id, so.user_id)
        # The purchase user can also edit the PR and confirm it
        purchase_pr = pr.with_user(self.purchaseperson)
        with Form(purchase_pr) as pr_form:
            pr_form.user_id = self.purchaseperson
        purchase_pr.action_in_progress()
        # Now the sale user can still read the PR
        with Form(pr) as pr_form:
            self.assertEqual(pr_form.state, "in_progress")
        # Also the overseers can read the PR
        with Form(pr.with_user(self.sale_overseer)) as pr_form:
            self.assertEqual(pr_form.sale_user_id, self.env.user)
        with Form(pr.with_user(self.full_overseer)) as pr_form:
            self.assertEqual(pr_form.sale_user_id, self.env.user)
        # But the sale people cannot edit it
        with self.assertRaises(AccessError), Form(pr) as pr_form:
            pr_form.user_id = self.env.user
        with self.assertRaises(AccessError), Form(
            pr.with_user(self.sale_overseer)
        ) as pr_form:
            pr_form.user_id = self.env.user
        # Although the full overseer can
        with Form(pr.with_user(self.full_overseer)) as pr_form:
            pr_form.user_id = self.full_overseer
        view = so.fields_view_get(view_type="form")
        doc = etree.XML(view["arch"])
        query = "//div[@id='warning_order_lines_notsync']"
        with Form(so) as so_form:
            with so_form.order_line.edit(0) as sol_f:
                sol_f.product_uom_qty = 11
                self.assertFalse(so_form.purchase_requisition_sync_warning)
            # Review in the view the warning div
            for item in doc.xpath(query):
                stri = json.loads(item.attrib["modifiers"])
                self.assertTrue(stri["invisible"][0])
        with Form(so) as so_form:
            with so_form.order_line.edit(0) as sol_f:
                sol_f.product_id = self.products[1]
                self.assertFalse(not so_form.purchase_requisition_sync_warning)
            # Review in the view the warning div
            for item in doc.xpath(query):
                stri = json.loads(item.attrib["modifiers"])
                self.assertTrue(stri["invisible"][0])

    @users("test_salesperson")
    def test_create_sale_order_and_pr_related(self):
        # User creates a sale order
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.products[0]
            line_form.product_uom_qty = 10
        so = so_form.save()
        # User creates the related purchase requisition
        action = so.action_create_purchase_requisition()
        pr_form = Form(self.env[action["res_model"]].with_context(action["context"]))
        pr = pr_form.save()
        pr = pr.with_context(action["context"])
        with Form(pr) as pr_form:
            pr_form.user_id = self.env.user
            with pr_form.line_ids.edit(0) as linpr1:
                linpr1.product_qty = 23
        pr2 = pr_form.save()
        self.assertTrue(pr2.sale_order_sync_warning)
        act = so.action_view_purchase_requisitions()
        self.assertEqual(act["view_mode"], "form" or "tree")
        so.action_cancel()

    @users("test_salesperson")
    def test_draft_pr_auto_synced(self):
        # Salesperson creates a sale order
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.products[0]
            line_form.product_uom_qty = 10
        so = so_form.save()
        # Salesperson overseer creates the related purchase requisition
        action = so.with_user(self.sale_overseer).action_create_purchase_requisition()
        pr_form = Form(
            self.env[action["res_model"]]
            .with_context(action["context"])
            .with_user(self.sale_overseer)
        )
        self.assertFalse(pr_form.user_id)
        pr_form.user_id = self.purchaseperson
        pr = pr_form.save()
        # Lines on SO and PR are synced
        self.assertRecordValues(
            so.order_line,
            [
                {"product_id": self.products[0].id, "product_uom_qty": 10},
            ],
        )
        self.assertRecordValues(
            pr.line_ids,
            [
                {"product_id": self.products[0].id, "product_qty": 10},
            ],
        )
        self.assertFalse(so.purchase_requisition_sync_warning)
        self.assertFalse(pr.sale_order_sync_warning)
        # Salesperson edits the SO line and the PR is updated
        with Form(so) as so_form:
            with so_form.order_line.edit(0) as sol_f:
                sol_f.product_uom_qty = 11
        self.assertRecordValues(
            so.order_line,
            [
                {"product_id": self.products[0].id, "product_uom_qty": 11},
            ],
        )
        self.assertRecordValues(
            pr.line_ids,
            [
                {"product_id": self.products[0].id, "product_qty": 11},
            ],
        )
        self.assertFalse(so.purchase_requisition_sync_warning)
        self.assertFalse(pr.sale_order_sync_warning)
        # Purchaseperson confirms the PR; salesperson updates the SO; unsync happens
        pr.with_user(self.purchaseperson).action_in_progress()
        with Form(so) as so_form:
            with so_form.order_line.edit(0) as sol_f:
                sol_f.product_uom_qty = 12
        self.assertRecordValues(
            so.order_line,
            [
                {"product_id": self.products[0].id, "product_uom_qty": 12},
            ],
        )
        self.assertRecordValues(
            pr.line_ids,
            [
                {"product_id": self.products[0].id, "product_qty": 11},
            ],
        )
        self.assertTrue(so.purchase_requisition_sync_warning)
        self.assertTrue(pr.sale_order_sync_warning)
        # Purchaseperson got notified of the unsync
        self.assertRecordValues(
            pr.activity_ids,
            [
                {
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "res_id": pr.id,
                    "user_id": self.purchaseperson.id,
                }
            ],
        )
