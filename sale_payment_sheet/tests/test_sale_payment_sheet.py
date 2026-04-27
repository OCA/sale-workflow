# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, new_test_user, tagged
from odoo.tests.common import users
from odoo.tools import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSaleInvoicePayment(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Archive all reconciliation models to avoid them interfering with the tests
        cls.env["account.reconcile.model"].search([]).active = False
        # Although it would be appropriate to create a cash journal for each user,
        # we will use default_journal_cash to simplify the test and avoid creating one.
        cls.journal_cash_user = cls.company_data["default_journal_cash"]
        cls.user = new_test_user(
            cls.env,
            # Remove time zone from user to avoid to time local representation
            tz=False,
            login="test-user",
            groups="account.group_account_user,base.group_no_one",
            commercial_journal_ids=cls.journal_cash_user.ids,
        )
        cls.wizard_obj = cls.env["sale.invoice.payment.wiz"]
        cls.SalePaymentSheet = cls.env["sale.payment.sheet"]
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.account_invoice = cls.company_data["default_account_revenue"]
        cls.invoice1 = cls.init_invoice(
            "out_invoice",
            partner=cls.partner,
            post=True,
            amounts=[100],
        )
        cls.invoice2 = cls.init_invoice(
            "out_invoice",
            partner=cls.partner,
            post=True,
            amounts=[100],
        )
        cls.refund1 = cls.init_invoice(
            "out_refund",
            partner=cls.partner,
            post=True,
            amounts=[10],
        )

    @users("test-user")
    def test_payment_wizard(self):
        wiz_form = Form(
            self.env["sale.invoice.payment.wiz"].with_context(
                active_model="account.move",
                active_ids=(self.invoice1 + self.invoice2).ids,
            )
        )
        wiz = wiz_form.save()
        wiz.wiz_line_ids.is_selected = True
        wiz.amount = 150.00
        self.assertEqual(wiz.partner_id, self.partner)
        self.assertEqual(wiz.journal_id, self.journal_cash_user)
        self.assertEqual(len(wiz.wiz_line_ids), 2)
        self.assertIn(self.invoice1, wiz.wiz_line_ids.mapped("invoice_id"))
        self.assertIn(self.invoice2, wiz.wiz_line_ids.mapped("invoice_id"))
        self.assertNotIn(self.refund1, wiz.wiz_line_ids.mapped("invoice_id"))
        action = wiz.create_sale_invoice_payment_sheet()
        sheet = self.SalePaymentSheet.browse(action["res_id"])
        self.assertEqual(len(sheet.line_ids), 2)
        line_partial_payment = sheet.line_ids.filtered(
            lambda ln: ln.transaction_type == "partial"
        )
        self.assertTrue(line_partial_payment)
        self.assertEqual(line_partial_payment.invoice_id, self.invoice2)
        line_full_payment = sheet.line_ids.filtered(
            lambda ln: ln.transaction_type == "full"
        )
        self.assertTrue(line_full_payment)
        self.assertEqual(line_full_payment.invoice_id, self.invoice1)
        self.assertEqual(sheet.amount_total, 150.00)

    def _create_payment_sheet(self):
        sheet_form = Form(self.SalePaymentSheet.with_user(self.user))
        for index, invoice in enumerate(self.invoice1 + self.invoice2):
            with sheet_form.line_ids.new() as line_sheet:
                line_sheet.partner_id = invoice.partner_id
                line_sheet.invoice_id = invoice
                # Only write for partial amount payed, by default the
                # amount line is total amount residual
                if index > 0:
                    line_sheet.amount = 50.0
        return sheet_form.save()

    @freeze_time("2021-01-01 09:30:00")
    def test_manual_payment_sheet(self):
        sheet = self._create_payment_sheet()
        self.assertEqual(sheet.user_id, self.user)
        self.assertEqual(sheet.journal_id, self.journal_cash_user)
        self.assertEqual(len(sheet.line_ids), 2)
        line_partial_payment = sheet.line_ids.filtered(
            lambda ln: ln.transaction_type == "partial"
        )
        self.assertTrue(line_partial_payment)
        self.assertEqual(line_partial_payment.invoice_id, self.invoice2)
        line_full_payment = sheet.line_ids.filtered(
            lambda ln: ln.transaction_type == "full"
        )
        self.assertTrue(line_full_payment)
        self.assertEqual(line_full_payment.invoice_id, self.invoice1)
        self.assertEqual(
            sheet.name,
            "{} - {} - {}".format(
                sheet.date.strftime("%Y.%m.%d"),
                sheet.journal_id.name,
                sheet.user_id.name,
            ),
        )
        self.assertEqual(
            line_partial_payment.name,
            "[{}] - {} - {} - ({})".format(
                "09:30",
                line_partial_payment.sheet_id.user_id.name,
                line_partial_payment.invoice_id.name,
                dict(
                    line_partial_payment._fields[
                        "transaction_type"
                    ]._description_selection(line_partial_payment.env)
                ).get(line_partial_payment.transaction_type),
            ),
        )

    def test_payment_sheet_confirm(self):
        sheet = self._create_payment_sheet()
        sheet.button_confirm_sheet()
        self.assertTrue(sheet.statement_id)
        self.assertEqual(len(sheet.line_ids.mapped("statement_line_id")), 2)

    @mute_logger("odoo.models.unlink")
    def test_payment_sheet_reopen(self):
        sheet = self._create_payment_sheet()
        sheet.button_confirm_sheet()
        sheet.button_reopen()
        self.assertFalse(sheet.statement_id)

    def test_payment_sheet_unlink(self):
        sheet = self._create_payment_sheet()
        sheet.button_confirm_sheet()
        with self.assertRaises(UserError):
            sheet.unlink()

    def test_payment_sheet_line_unlink(self):
        sheet = self._create_payment_sheet()
        sheet.button_confirm_sheet()
        with self.assertRaises(UserError):
            sheet.line_ids.unlink()

    def test_button_bank_statement(self):
        sheet = self._create_payment_sheet()
        sheet.button_bank_statement()

    def test_payment_sheet_invoice_constraint(self):
        # You can not add full invoice payed more than one time.
        sheet = self._create_payment_sheet()
        sheet_form = Form(sheet)
        with sheet_form.line_ids.new() as line_sheet:
            line_sheet.partner_id = self.partner
            line_sheet.invoice_id = self.invoice1
        with self.assertRaises(ValidationError):
            sheet_form.save()

    def test_payment_sheet_report(self):
        sheet = self._create_payment_sheet()
        report = self.env["ir.actions.report"]._get_report_from_name(
            "sale_payment_sheet.report_sale_payment_sheet"
        )
        res = report._render_qweb_text(report, sheet.ids)
        self.assertRegex(str(res[0]), self.invoice1.name)
        self.assertRegex(str(res[0]), self.invoice2.name)
        self.assertRegex(str(res[0]), self.partner.name)
