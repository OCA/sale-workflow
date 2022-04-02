# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrderLineDates(TransactionCase):
    def setUp(self):
        super().setUp()
        # Configure Contact Stages
        self.stage_active = self.env.ref("partner_stage.partner_stage_active")
        self.stage_active.is_default = False
        self.stage_active.approved_sale = True
        self.stage_draft = self.env.ref("partner_stage.partner_stage_draft")
        self.stage_draft.is_default = True
        self.stage_draft.approved_sale = False
        # Enable demo rule
        self.env.ref("sale_partner_approval.excep_partner_approved").active = True

    def test_flow_sale_order_approved(self):
        # New Customer is not approved for sales
        customer = self.env["res.partner"].create(
            {"name": "A Customer", "candidate_sale": True}
        )
        self.assertFalse(customer.sale_ok)
        # Sales Order for not approved customer can't be confirmed
        # It resturn a popu dialog for sale.exception.confirm
        order = self.env["sale.order"].create({"partner_id": customer.id})
        res = order.action_confirm()
        self.assertEqual(res["res_model"], "sale.exception.confirm")
        # Approve the customer for sales
        # (consider the case with Tier Validation, and Validate partner stage change)
        if hasattr(customer, "review_ids"):
            customer.request_validation()
            customer.invalidate_cache()  # Needed to refresh review_ids field
            customer.review_ids.write({"status": "approved"})
        customer.stage_id = self.env.ref("partner_stage.partner_stage_active")
        self.assertTrue(customer.sale_ok)
        # Sales Order for approved customer can be confirmed
        # (consider the case with Tier Validation, and Validate partner stage change)
        if hasattr(order, "review_ids"):
            order.request_validation()
            order.invalidate_cache()  # Needed to refresh review_ids field
            order.review_ids.write({"status": "approved"})
        res = order.action_confirm()
        self.assertIn(order.state, ["sale", "done"])
