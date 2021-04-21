# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import odoo.tests.common as common
from odoo import fields


class PurchaseVerifiedCase(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.product1 = self.env.ref("product.product_product_9")
        self.product2 = self.env.ref("product.product_product_11")
        self.partner = self.env.ref("base.res_partner_2")

        self.data = {
            "rating": 5,
            "feedback": "test",
            "res_id": self.product1.id,
            "res_model_id": self.env.ref("product.model_product_product").id,
            "partner_id": self.partner.id,
            "consumed": True,
        }

        self.record = self.env["rating.rating"].create(self.data)

    def test_verified(self):
        self.assertFalse(self.record.purchase_verified)
        invoice = self._create_invoice()
        res = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product1.id),
                ("partner_id", "=", self.partner.id),
                ("res_model", "=", "product.product"),
            ],
            limit=1,
        )
        self.assertTrue(res)
        # the invoice was not paid so the purchase is not verified
        self.assertFalse(res.purchase_verified)
        self._make_payment(invoice)
        data = self.data.copy()
        data["res_id"] = self.product2.id
        self.record = self.env["rating.rating"].create(data)
        res = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product2.id),
                ("partner_id", "=", self.partner.id),
                ("res_model", "=", "product.product"),
            ],
            limit=1,
        )
        self.assertTrue(res.purchase_verified)

    def test_verified2(self):
        """
        this test makes sure that the 'verified' field is true
        only if res_model is product.product
        """
        invoice = self._create_invoice()
        self._make_payment(invoice)

        data = self.data.copy()
        data["res_id"] = self.product1.id
        data["res_model_id"] = self.env.ref("base.model_res_partner").id
        data["res_model"] = "res.partner"
        data["partner_id"] = self.partner.id
        data["feedback"] = "does not work"
        self.record = self.env["rating.rating"].create(data)
        res = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product1.id),
                ("partner_id", "=", self.partner.id),
                ("res_model", "=", "res.partner"),
            ],
            limit=1,
        )
        self.assertTrue(res)
        self.assertFalse(res.purchase_verified)

    def _create_invoice(self):
        product1_categ = self.product1.categ_id.property_account_expense_categ_id
        product2_categ = self.product2.categ_id.property_account_expense_categ_id
        values = {
            "partner_id": self.partner.id,
            "invoice_date": fields.Date.today(),
            "move_type": "out_invoice",
            "invoice_line_ids": [
                (
                    0,
                    False,
                    {
                        "product_id": self.product2.id,
                        "quantity": 10,
                        "price_unit": 1250,
                        "account_id": product2_categ,
                        "name": self.product2.display_name,
                    },
                ),
                (
                    0,
                    False,
                    {
                        "product_id": self.product1.id,
                        "quantity": 10,
                        "price_unit": 1250,
                        "account_id": product1_categ,
                        "name": self.product1.display_name,
                    },
                ),
            ],
        }
        invoice = self.env["account.move"].create(values)
        invoice.state = "posted"
        return invoice

    def _make_payment(self, invoice, journal=False, amount=False):
        """
        Make payment for given invoice
        :param invoice: account.invoice recordset
        :param amount: float
        :return: bool
        """
        ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
        wizard_obj = self.env["account.payment.register"].with_context(ctx)
        self.bank_journal_euro = self.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        if journal:
            register_payments.write({"journal_id": journal.id})
        if amount:
            register_payments.write({"amount": amount})
        register_payments.action_create_payments()
