# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, TransactionCase


@freeze_time("2021-01-01 09:30:00")
class TestSaleInvoicePayment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Remove time zone from user to avoid to time local representation
        cls.env.user.partner_id.tz = False
        cls.wizard_obj = cls.env["sale.invoice.payment.wiz"]
        cls.SalePaymentSheet = cls.env["sale.payment.sheet"]
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Bank journal", "type": "bank", "code": "test"}
        )
        account_type_income = cls.env.ref("account.data_account_type_revenue")
        cls.account_invoice = cls.env["account.account"].create(
            {
                "code": "test",
                "name": "Test account",
                "user_type_id": account_type_income.id,
            }
        )
        cls.invoice1 = cls._create_invoice(cls)
        cls.invoice2 = cls._create_invoice(cls)
        (cls.invoice1 + cls.invoice2).action_post()

    def _create_invoice(self):
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.partner
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.name = "invoice test"
                line_form.account_id = self.account_invoice
                line_form.quantity = 1.0
                line_form.price_unit = 100.00
        return invoice_form.save()

    def test_payment_wizard(self):
        PaymentWiz = self.env["sale.invoice.payment.wiz"].with_context(
            active_model="account.move",
            active_ids=(self.invoice1 + self.invoice2).ids,
        )
        with Form(PaymentWiz) as wiz_form:
            wiz_form.journal_id = self.bank_journal
            wiz_form.amount = 150.00
        wiz = wiz_form.save()
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
        with Form(self.SalePaymentSheet) as sheet_form:
            sheet_form.journal_id = self.bank_journal
            for index, invoice in enumerate(self.invoice1 + self.invoice2):
                with sheet_form.line_ids.new() as line_sheet:
                    line_sheet.partner_id = self.partner
                    line_sheet.invoice_id = invoice
                    line_sheet.ref = "REF{}".format(line_sheet.id)
                    # Only write for partial amount payed, by default the
                    # amount line is total amount residual
                    if index > 0:
                        line_sheet.amount = 50.0
        return sheet_form.save()

    def test_manual_payment_sheet(self):
        sheet = self._create_payment_sheet()
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
        with self.assertRaises(ValidationError):
            with Form(sheet) as sheet_form:
                with sheet_form.line_ids.new() as line_sheet:
                    line_sheet.partner_id = self.partner
                    line_sheet.invoice_id = self.invoice1
            sheet_form.save()
