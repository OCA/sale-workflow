import odoo.tests.common as common
from odoo.tests import Form, tagged


@tagged("post_install", "-at_install")
class TestAccountInvoice(common.TransactionCase):
    def test_account_invoice_create(self):
        self.journal_1 = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        self.journal_2 = self.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        self.partner = self.env.ref("base.res_partner_1")
        self.action_invoice_1 = self.journal_1.action_create_new()
        self.action_invoice_2 = self.journal_2.action_create_new()
        new_invoice_1 = Form(
            self.env["account.move"].with_context(self.action_invoice_1["context"]),
            view=self.env["ir.model.data"].xmlid_to_res_id("account.view_move_form"),
        )
        new_invoice_2 = Form(
            self.env["account.move"].with_context(self.action_invoice_2["context"]),
            view=self.env["ir.model.data"].xmlid_to_res_id("account.view_move_form"),
        )
        new_invoice_1.partner_id = self.partner
        new_invoice_2.partner_id = self.partner
        new_invoice_1.save()
        new_invoice_2.save()
        self.assertEqual(self.journal_1.id, new_invoice_1.journal_id.id)
        self.assertEqual(self.journal_2.id, new_invoice_2.journal_id.id)
