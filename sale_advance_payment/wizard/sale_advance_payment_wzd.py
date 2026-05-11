# Copyright 2017 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountVoucherWizard(models.TransientModel):
    _name = "account.voucher.wizard"
    _description = "Account Voucher Wizard"

    order_id = fields.Many2one("sale.order", required=True)
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        required=True,
        domain=[("type", "in", ("bank", "cash"))],
    )
    payment_method_line_id = fields.Many2one(
        "account.payment.method.line",
        string="Payment Method",
        readonly=False,
        store=True,
        copy=False,
        compute="_compute_payment_method_line_id",
        domain="[('id', 'in', available_payment_method_line_ids)]",
        help="Manual: Pay or Get paid by any method outside of Odoo.\n"
        "Payment Providers: Each payment provider has its own Payment Method. "
        "Request a transaction on/to a card thanks to a payment token saved "
        "by the partner when buying or subscribing online.\n"
        "Check: Pay bills by check and print it from Odoo.\n"
        "Batch Deposit: Collect several customer checks at once generating and "
        "submitting a batch deposit to your bank. Module account_batch_payment "
        "is necessary.\n"
        "SEPA Credit Transfer: Pay in the SEPA zone by submitting a SEPA "
        "Credit Transfer file to your bank. Module account_sepa is necessary.\n"
        "SEPA Direct Debit: Get paid in the SEPA zone thanks to a mandate your "
        "partner will have granted to you. Module account_sepa is necessary.\n",
    )
    available_payment_method_line_ids = fields.Many2many(
        "account.payment.method.line", compute="_compute_payment_method_line_fields"
    )
    journal_currency_id = fields.Many2one(
        "res.currency",
        "Journal Currency",
        store=True,
        readonly=False,
        compute="_compute_get_journal_currency",
    )
    currency_id = fields.Many2one("res.currency", "Currency")
    amount_total = fields.Monetary()
    amount_advance = fields.Monetary(
        "Amount advanced", required=True, currency_field="journal_currency_id"
    )
    date = fields.Date(required=True, default=fields.Date.context_today)
    currency_amount = fields.Monetary(
        "Curr. amount",
        currency_field="currency_id",
        compute="_compute_currency_amount",
        store=True,
    )
    payment_ref = fields.Char("Ref.")
    payment_type = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        default="inbound",
        required=True,
    )

    @api.depends("available_payment_method_line_ids")
    def _compute_payment_method_line_id(self):
        """Compute the 'payment_method_line_id' field.
        This field is not computed in '_compute_payment_method_line_fields'
        because it's a stored editable one.
        """
        for pay in self:
            available_payment_method_lines = pay.available_payment_method_line_ids

            # Select the first available one by default.
            if pay.payment_method_line_id in available_payment_method_lines:
                pay.payment_method_line_id = pay.payment_method_line_id
            elif available_payment_method_lines:
                pay.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                pay.payment_method_line_id = False

    @api.depends("payment_type", "journal_id", "currency_id")
    def _compute_payment_method_line_fields(self):
        for pay in self:
            pay.available_payment_method_line_ids = (
                pay.journal_id._get_available_payment_method_lines(pay.payment_type)
            )
            to_exclude = pay._get_payment_method_codes_to_exclude()
            if to_exclude:
                pay.available_payment_method_line_ids = (
                    pay.available_payment_method_line_ids.filtered(
                        lambda line, to_exclude=to_exclude: line.code not in to_exclude
                    )
                )

    def _get_payment_method_codes_to_exclude(self):
        return []

    @api.depends("journal_id")
    def _compute_get_journal_currency(self):
        for wzd in self:
            wzd.journal_currency_id = (
                wzd.journal_id.currency_id.id
                or wzd.journal_id.company_id.currency_id.id
            )

    @api.constrains("amount_advance")
    def check_amount(self):
        if self.amount_advance <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be positive."))
        if self.env.context.get("active_id", False):
            if self.payment_type == "inbound":
                if (
                    float_compare(
                        self.currency_amount,
                        self.order_id.amount_residual,
                        precision_digits=2,
                    )
                    > 0
                ):
                    raise exceptions.ValidationError(
                        _(
                            "Inbound amount of advance is greater than residual "
                            "amount on sale"
                        )
                    )
            else:
                paid_in_advanced = self.order_id.amount_total - self.amount_total
                if (
                    float_compare(
                        self.currency_amount,
                        paid_in_advanced,
                        precision_digits=2,
                    )
                    > 0
                ):
                    raise exceptions.ValidationError(
                        _(
                            "Outbound amount of advance is greater than the "
                            "advanced paid amount"
                        )
                    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale_ids = self.env.context.get("active_ids", [])
        if not sale_ids:
            return res
        sale_id = fields.first(sale_ids)
        sale = self.env["sale.order"].browse(sale_id)
        if "amount_total" in fields_list:
            res.update(
                {
                    "order_id": sale.id,
                    "amount_total": sale.amount_residual,
                    "currency_id": sale.pricelist_id.currency_id.id
                    or sale.currency_id.id,
                }
            )

        return res

    @api.depends("journal_id", "date", "amount_advance")
    def _compute_currency_amount(self):
        for wzd in self:
            if wzd.journal_currency_id != wzd.currency_id:
                amount_advance = wzd.journal_currency_id._convert(
                    wzd.amount_advance,
                    wzd.currency_id,
                    wzd.order_id.company_id,
                    wzd.date or fields.Date.today(),
                )
            else:
                amount_advance = wzd.amount_advance
            wzd.currency_amount = amount_advance

    def _prepare_payment_vals(self, sale):
        partner_id = sale.partner_invoice_id.commercial_partner_id.id
        if self.amount_advance < 0.0:
            raise UserError(
                _(
                    "The amount to advance must always be positive. "
                    "Please use the payment type to indicate if this "
                    "is an inbound or an outbound payment."
                )
            )

        return {
            "date": self.date,
            "amount": self.amount_advance,
            "payment_type": self.payment_type,
            "partner_type": "customer",
            "ref": self.payment_ref or sale.name,
            "journal_id": self.journal_id.id,
            "currency_id": self.journal_currency_id.id,
            "partner_id": partner_id,
            "payment_method_line_id": self.payment_method_line_id.id,
        }

    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        self.ensure_one()
        payment_obj = self.env["account.payment"]
        sale_obj = self.env["sale.order"]
        sale_ids = self.env.context.get("active_ids", [])
        if sale_ids:
            sale_id = fields.first(sale_ids)
            sale = sale_obj.browse(sale_id)
            payment_vals = self._prepare_payment_vals(sale)
            payment = payment_obj.create(payment_vals)
            sale.account_payment_ids |= payment
            payment.action_post()

        return {
            "type": "ir.actions.act_window_close",
        }
