##############################################################################
#
#    Copyright (C) 2015 Comunitea Servicios Tecnológicos All Rights Reserved
#    $Omar Castiñeira Saaevdra <omar@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import _, api, exceptions, fields, models


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
    journal_currency_id = fields.Many2one(
        "res.currency",
        "Journal Currency",
        store=True,
        readonly=False,
        compute="_compute_get_journal_currency",
    )
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)
    amount_total = fields.Monetary("Amount total", readonly=True)
    amount_advance = fields.Monetary(
        "Amount advanced", required=True, currency_field="journal_currency_id"
    )
    date = fields.Date("Date", required=True, default=fields.Date.context_today)
    currency_amount = fields.Monetary(
        "Curr. amount", readonly=True, currency_field="currency_id"
    )
    payment_ref = fields.Char("Ref.")

    @api.depends("journal_id")
    def _compute_get_journal_currency(self):
        for wzd in self:
            wzd.journal_currency_id = (
                wzd.journal_id.currency_id.id or self.env.user.company_id.currency_id.id
            )

    @api.constrains("amount_advance")
    def check_amount(self):
        if self.amount_advance <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be positive."))
        if self.env.context.get("active_id", False):
            if self.amount_advance > self.order_id.amount_residual:
                raise exceptions.ValidationError(
                    _("Amount of advance is greater than residual amount on sale")
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
                    "currency_id": sale.pricelist_id.currency_id.id,
                }
            )

        return res

    @api.onchange("journal_id", "date", "amount_advance")
    def onchange_date(self):
        if self.journal_currency_id != self.currency_id:
            amount_advance = self.journal_currency_id._convert(
                self.amount_advance,
                self.currency_id,
                self.order_id.company_id,
                self.date or fields.Date.today(),
            )
        else:
            amount_advance = self.amount_advance
        self.currency_amount = amount_advance

    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        self.ensure_one()
        payment_obj = self.env["account.payment"]
        sale_obj = self.env["sale.order"]

        sale_ids = self.env.context.get("active_ids", [])
        if sale_ids:
            sale_id = fields.first(sale_ids)
            sale = sale_obj.browse(sale_id)

            partner_id = sale.partner_invoice_id.commercial_partner_id.id
            payment_res = {
                "date": self.date,
                "amount": self.amount_advance,
                "payment_type": "inbound",
                "partner_type": "customer",
                "ref": self.payment_ref or sale.name,
                "journal_id": self.journal_id.id,
                "currency_id": self.journal_currency_id.id,
                "partner_id": partner_id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
            payment = payment_obj.create(payment_res)
            sale.account_payment_ids |= payment
            payment.action_post()

        return {
            "type": "ir.actions.act_window_close",
        }
