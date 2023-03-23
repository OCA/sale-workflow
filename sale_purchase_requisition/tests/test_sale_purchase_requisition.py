# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo.tests.common import Form, TransactionCase, new_test_user, users


class TestSalePurchaseRequisition(TransactionCase):
    def setUp(self):
        super().setUp()
        self.products = self.env["product.product"].create(
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
        self.salesman = new_test_user(
            self.env, "test_salesman", groups="sales_team.group_sale_salesman"
        )
        self.customer = self.env["res.partner"].create(
            {
                "name": "test customer",
            }
        )

    @users("test_salesman")
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
        # self.assertEqual(action["res_id"], pr.id)
        self.assertEqual(action["res_model"], pr._name)
        pr = pr.with_context(action["context"])
        with Form(pr) as pr_form:
            pr_form.user_id = self.env.user
        self.assertEqual(pr.user_id, so.user_id)
        # The user confirms the PR and cannot edit SO anymore
        pr.action_in_progress()
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

    @users("test_salesman")
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
        self.assertTrue(pr2.purchase_requisition_sync_warning)
        act = so.action_view_purchase_requisitions()
        self.assertEqual(act["view_mode"], "form" or "tree")
        so.action_cancel()
