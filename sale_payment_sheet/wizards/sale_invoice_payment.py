# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleInvoicePaymentWiz(models.TransientModel):
    _name = "sale.invoice.payment.wiz"
    _description = "Sale invoice payment wizard"

    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=False,
        default=lambda self: self.env.user,
    )
    commercial_journal_ids = fields.Many2many(related="user_id.commercial_journal_ids")
    currency_id = fields.Many2one(
        "res.currency", compute="_compute_currency", string="Currency"
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal", string="Journal", required=True,
    )
    amount = fields.Monetary(
        currency_field="currency_id", string="Amount", required=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super(SaleInvoicePaymentWiz, self).default_get(fields_list)
        invoices = self.env["account.move"].browse(self.env.context.get("active_ids"))
        res["amount"] = sum(invoices.mapped("amount_residual"))
        return res

    @api.depends("journal_id")
    def _compute_currency(self):
        for wiz in self:
            wiz.currency_id = wiz.journal_id.currency_id

    def create_sale_invoice_payment_sheet(self):
        invoices = (
            self.env["account.move"]
            .browse(self.env.context.get("active_ids"))
            .filtered(
                lambda inv: inv.state == "posted"
                and inv.invoice_payment_state != "paid"
            )
        )
        if not invoices:
            return
        # Search an open payment sheet or create one if not exists
        SalePaymentSheet = self.env["sale.payment.sheet"]
        sheet = SalePaymentSheet.search(
            [
                ("state", "=", "open"),
                ("user_id", "=", self.env.user.id),
                ("journal_id", "=", self.journal_id.id),
                ("date", "=", fields.Date.today()),
            ]
        )
        if not sheet:
            sheet = SalePaymentSheet.create(
                {
                    "user_id": self.env.user.id,
                    "journal_id": self.journal_id.id,
                    "date": fields.Date.today(),
                }
            )
        for invoice in invoices:
            if not self.amount:
                break
            sheet_line = sheet.line_ids.filtered(lambda ln: ln.invoice_id == invoice)
            amount_pay = (
                invoice.amount_residual
                if self.amount >= invoice.amount_residual
                else self.amount
            )
            # TODO: What to do if a line has been finded
            if sheet_line:
                sheet_line.amount = amount_pay
            else:
                sheet.line_ids = [
                    (
                        0,
                        0,
                        {
                            "amount": amount_pay,
                            "partner_id": invoice.partner_id.id,
                            "invoice_id": invoice.id,
                        },
                    )
                ]
            self.amount -= amount_pay
        return sheet
