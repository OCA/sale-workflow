# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class SalePaymentSheet(models.Model):
    _name = "sale.payment.sheet"
    _description = "Sale Payment Sheet"
    _order = "date desc, id desc"
    _inherit = ["mail.thread"]
    _check_company_auto = True

    name = fields.Char(
        string="Reference",
        states={"open": [("readonly", False)]},
        copy=False,
        compute="_compute_name",
        readonly=True,
        store=True,
    )
    reference = fields.Char(
        string="External Reference",
        states={"open": [("readonly", False)]},
        copy=False,
        readonly=True,
    )
    date = fields.Date(
        required=True,
        states={"confirm": [("readonly", True)]},
        index=True,
        copy=False,
        default=fields.Date.context_today,
    )
    state = fields.Selection(
        [("open", "New"), ("confirm", "Validated")],
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        default="open",
    )
    currency_id = fields.Many2one(
        "res.currency", compute="_compute_currency", string="Currency"
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        states={"confirm": [("readonly", True)]},
        default=lambda self: self._default_journal(),
    )
    commercial_journal_ids = fields.Many2many(related="user_id.commercial_journal_ids")
    company_id = fields.Many2one(
        "res.company",
        related="journal_id.company_id",
        string="Company",
        store=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        "sale.payment.sheet.line",
        "sheet_id",
        string="Sheet lines",
        states={"confirm": [("readonly", True)]},
        copy=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=False,
        default=lambda self: self.env.user,
    )
    statement_id = fields.Many2one(
        comodel_name="account.bank.statement", string="Bank statement"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute="_compute_amount_total"
    )

    @api.depends("line_ids.amount")
    def _compute_amount_total(self):
        """ Summarize total amount lines, this field already is signed
        depending on invoice type.
        """
        for sheet in self:
            sheet.amount_total = sum(sheet.line_ids.mapped("amount"))

    @api.model
    def _default_journal(self):
        return self.env.user.commercial_journal_ids[:1]

    @api.depends("journal_id.currency_id")
    def _compute_currency(self):
        for sheet in self:
            sheet.currency_id = (
                sheet.journal_id.currency_id or sheet.company_id.currency_id
            )

    @api.depends("journal_id", "user_id", "date")
    def _compute_name(self):
        for sheet in self:
            sheet.name = "{} - {} - {}".format(
                sheet.date and sheet.date.strftime("%Y.%m.%d"),
                sheet.journal_id.name,
                sheet.user_id.name,
            )

    def unlink(self):
        for sheet in self:
            if sheet.state != "open":
                raise UserError(
                    _("You can not delete a sheet if has related journal items.")
                )
        return super().unlink()

    def button_confirm_sheet(self):
        sheets = self.filtered(lambda r: r.state == "open")
        BankStatement = self.env["account.bank.statement"].sudo()
        BankStatementLine = self.env["account.bank.statement.line"].sudo()
        for sheet in sheets:
            statement = BankStatement.create(
                {
                    "name": sheet.name,
                    "date": sheet.date,
                    "journal_id": sheet.journal_id.id,
                    "user_id": sheet.user_id.id,
                }
            )
            for line in sheet.line_ids:
                vals = {
                    "name": line.name,
                    "date": line.date,
                    "amount": line.amount,
                    "partner_id": line.partner_id.id,
                    "ref": line.ref,
                    "note": line.note,
                    "sequence": line.sequence,
                    "statement_id": statement.id,
                }
                if line.invoice_id.type == "out_refund" and line.amount > 0.0:
                    # convert to negative amounts if user pays a refund out
                    # invoice with a positive amount.
                    vals["amount"] = -line.amount
                statement_line = BankStatementLine.create(vals)
                line.statement_line_id = statement_line
            sheet.message_post(
                body=_("Sheet %s confirmed, bank statement were created.")
                % (statement.name,)
            )
            sheet.write({"state": "confirm", "statement_id": statement.id})

    def button_reopen(self):
        self.ensure_one()
        self_sudo = self.sudo()
        if self_sudo.statement_id.line_ids.filtered("journal_entry_ids"):
            raise UserError(
                _("You can not reopen a sheet that has any reconciled line.")
            )
        self_sudo.statement_id.unlink()
        self.state = "open"

    def button_bank_statement(self):
        """
        Action to open bank statement linked
        """
        self.ensure_one()
        return self.statement_id.get_formview_action()


class SalePaymentSheetLine(models.Model):
    _name = "sale.payment.sheet.line"
    _description = "Sale Payment Sheet Line"
    _order = "sheet_id desc, date, sequence, id desc"

    name = fields.Char(
        string="Label", compute="_compute_name", store=True, readonly=False
    )
    date = fields.Date(
        required=True,
        default=lambda self: self.env.context.get(
            "date", fields.Date.context_today(self)
        ),
    )
    sheet_id = fields.Many2one(
        "sale.payment.sheet",
        string="Sheet",
        index=True,
        required=True,
        ondelete="cascade",
    )
    statement_line_id = fields.Many2one(
        "account.bank.statement.line", string="Statement Line", index=True
    )
    amount = fields.Monetary(
        compute="_compute_amount",
        inverse="_inverse_amount",
        currency_field="journal_currency_id",
        store=True,
        readonly=False,
    )
    journal_currency_id = fields.Many2one(
        "res.currency",
        string="Journal's Currency",
        related="sheet_id.currency_id",
        help="Utility field to express amount currency",
        readonly=True,
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    ref = fields.Char(string="Reference")
    note = fields.Text(string="Notes")
    sequence = fields.Integer(
        index=True,
        help="Gives the sequence order when displaying a list of payment sheet lines.",
        default=1,
    )
    company_id = fields.Many2one(
        "res.company",
        related="sheet_id.company_id",
        string="Company",
        store=True,
        readonly=True,
    )
    state = fields.Selection(related="sheet_id.state", string="Status", readonly=True)
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")
    transaction_type = fields.Selection(
        [("partial", "Partial payment"), ("full", "Full payment")],
        compute="_compute_transaction_type",
        string="Transaction type",
    )

    @api.depends("amount", "invoice_id")
    def _compute_transaction_type(self):
        for line in self:
            amount = (
                line.amount if line.invoice_id.type == "out_invoice" else -line.amount
            )
            if float_compare(
                amount,
                line.invoice_id.amount_total,
                precision_digits=line.sheet_id.currency_id.decimal_places,
            ):
                line.transaction_type = "partial"
            else:
                line.transaction_type = "full"

    @api.depends("sheet_id.user_id", "invoice_id", "transaction_type")
    def _compute_name(self):
        for line in self:
            if not line.create_date:
                line.create_date = fields.Datetime.now()
            line.name = "[{}] - {} - {} - ({})".format(
                fields.Datetime.context_timestamp(line, line.create_date).strftime(
                    "%H:%M"
                ),
                line.sheet_id.user_id.name,
                line.invoice_id.name,
                dict(
                    line._fields["transaction_type"]._description_selection(line.env)
                ).get(line.transaction_type),
            )

    @api.depends("invoice_id")
    def _compute_amount(self):
        for line in self:
            amount = line.invoice_id.amount_residual
            line.amount = amount if line.invoice_id.type == "out_invoice" else -amount

    def _inverse_amount(self):
        for line in self:
            if line.invoice_id.type == "out_refund" and line.amount > 0.0:
                line.amount = -line.amount

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            # Allow to enter sheet line with an amount of 0,
            if line.journal_currency_id.is_zero(line.amount):
                raise ValidationError(
                    _("The amount of a cash transaction cannot be 0.")
                )

    def unlink(self):
        if self.filtered("statement_line_id"):
            raise UserError(
                _("You can not delete payment lines if have related statement lines.")
            )
        return super().unlink()
