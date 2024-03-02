# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_plan_ids = fields.One2many(
        comodel_name="sale.invoice.plan",
        inverse_name="sale_id",
        string="Invoice Plan",
        copy=False,
    )
    use_invoice_plan = fields.Boolean(
        default=False,
        copy=False,
    )
    invoice_plan_process = fields.Boolean(
        string="Invoice Plan In Process",
        compute="_compute_invoice_plan_process",
        help="At least one invoice plan line pending to create invoice",
    )
    invoice_plan_total_percent = fields.Float(
        compute="_compute_invoice_plan_total",
        string="Percent",
    )
    invoice_plan_total_amount = fields.Monetary(
        compute="_compute_invoice_plan_total",
        string="Total Amount",
    )
    # Reporting
    next_installment_id = fields.Many2one(
        "sale.invoice.plan",
        string="Next Installment To Invoice",
        compute="_compute_next_to_invoice_plan_id",
        store=True,
    )
    next_installment_date = fields.Date(
        related="next_installment_id.plan_date",
        string="Next Installment Date",
        store=True,
    )
    invoiced_installment_amount = fields.Monetary(
        compute="_compute_invoiced_installment_amount",
        store=True,
    )
    pending_installment_amount = fields.Monetary(
        compute="_compute_pending_installment_amount",
        store=True,
    )

    @api.depends("invoice_plan_ids.percent", "invoice_plan_ids.amount")
    def _compute_invoice_plan_total(self):
        for rec in self:
            installments = rec.invoice_plan_ids.filtered("installment")
            rec.invoice_plan_total_percent = sum(installments.mapped("percent"))
            rec.invoice_plan_total_amount = sum(installments.mapped("amount"))

    @api.depends(
        "use_invoice_plan",
        "state",
        "invoice_status",
        "invoice_plan_ids.invoiced",
    )
    def _compute_invoice_plan_process(self):
        for rec in self:
            has_invoice_plan = rec.use_invoice_plan and rec.invoice_plan_ids
            to_invoice = rec.invoice_plan_ids.filtered(lambda l: not l.invoiced)
            rec.invoice_plan_process = (
                rec.state == "sale"
                and has_invoice_plan
                and to_invoice
                and rec.invoice_status in ["to invoice", "no"]
            )

    @api.depends("invoice_plan_ids.invoice_move_ids", "invoice_plan_ids.invoiced")
    def _compute_next_to_invoice_plan_id(self):
        for sale in self:
            last_invoiced = sale.invoice_plan_ids.filtered("invoice_move_ids")[-1:]
            last_installment = last_invoiced.installment or 0
            next_to_invoice = sale.invoice_plan_ids.filtered(
                lambda x: x.installment == last_installment + 1
            )
            sale.next_installment_id = next_to_invoice

    @api.depends(
        "next_installment_id",
        "invoice_plan_ids.amount_invoiced",
        "invoice_plan_ids.invoice_move_ids.state",
    )
    def _compute_invoiced_installment_amount(self):
        for sale in self:
            # Invoice Plan computations are not always triggered when changes happen
            # So we need to force that recomputation
            sale.invoice_plan_ids._compute_invoiced()
            invoiced_plans = sale.invoice_plan_ids.filtered("invoiced")
            invoiced_amount = sum(invoiced_plans.mapped("amount_invoiced"))
            sale.invoiced_installment_amount = invoiced_amount

    @api.depends("invoice_plan_total_amount", "invoiced_installment_amount")
    def _compute_pending_installment_amount(self):
        for sale in self:
            sale.pending_installment_amount = (
                sale.invoice_plan_total_amount - sale.invoiced_installment_amount
            )

    @api.constrains("invoice_plan_ids")
    def _check_invoice_plan_total_percent(self):
        for rec in self:
            installments = rec.invoice_plan_ids.filtered("installment")
            invoice_plan_total_percent = sum(installments.mapped("percent"))
            if float_round(invoice_plan_total_percent, 0) > 100:
                raise UserError(_("Invoice plan total percentage must not exceed 100%"))

    @api.constrains("state")
    def _check_invoice_plan(self):
        for rec in self:
            if rec.state != "draft":
                if rec.invoice_plan_ids.filtered(lambda l: not l.percent):
                    raise ValidationError(
                        _("Please fill percentage for all invoice plan lines")
                    )

    def action_confirm(self):
        if self.filtered(lambda r: r.use_invoice_plan and not r.invoice_plan_ids):
            raise UserError(_("Use Invoice Plan selected, but no plan created"))
        return super().action_confirm()

    def create_invoice_plan(
        self, num_installment, installment_date, interval, interval_type, advance
    ):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        invoice_plans = []
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Sales Invoice Plan Percent")
        percent = float_round(1.0 / num_installment * 100, prec)
        percent_last = 100 - (percent * (num_installment - 1))
        # Advance
        if advance:
            vals = {
                "installment": 0,
                "plan_date": installment_date,
                "invoice_type": "advance",
                "percent": 0.0,
            }
            invoice_plans.append((0, 0, vals))
            installment_date = self._next_date(
                installment_date, interval, interval_type
            )
        # Normal
        for i in range(num_installment):
            this_installment = i + 1
            if num_installment == this_installment:
                percent = percent_last
            vals = {
                "installment": this_installment,
                "plan_date": installment_date,
                "invoice_type": "installment",
                "percent": percent,
            }
            invoice_plans.append((0, 0, vals))
            installment_date = self._next_date(
                installment_date, interval, interval_type
            )
        self.write({"invoice_plan_ids": invoice_plans})
        return True

    def remove_invoice_plan(self):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        return True

    @api.model
    def _next_date(self, installment_date, interval, interval_type):
        installment_date = fields.Date.from_string(installment_date)
        if interval_type == "month":
            next_date = installment_date + relativedelta(months=+interval)
        elif interval_type == "year":
            next_date = installment_date + relativedelta(years=+interval)
        else:
            next_date = installment_date + relativedelta(days=+interval)
        next_date = fields.Date.to_string(next_date)
        return next_date

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)
        for sale in self.filtered(lambda s: s.use_invoice_plan):
            next_installment = sale.invoice_plan_ids.filtered(
                lambda x: x.to_invoice and x.invoice_type == "installment"
            )[:1]
            if next_installment:
                sale_moves = moves & sale.invoice_ids
                for move in sale_moves:
                    next_installment._compute_new_invoice_quantity(move)
                    move.invoice_date = next_installment.plan_date
                    move._compute_date()
        return moves
