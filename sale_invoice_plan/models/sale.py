# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_plan_ids = fields.One2many(
        comodel_name="sale.invoice.plan",
        inverse_name="sale_id",
        string="Inovice Plan",
        copy=False,
    )
    use_invoice_plan = fields.Boolean(
        string="Use Invoice Plan", default=False, copy=False,
    )
    ip_invoice_plan = fields.Boolean(
        string="Invoice Plan In Process",
        compute="_compute_ip_invoice_plan",
        help="At least one invoice plan line pending to create invoice",
    )

    def _compute_ip_invoice_plan(self):
        for rec in self:
            has_invoice_plan = rec.use_invoice_plan and rec.invoice_plan_ids
            to_invoice = rec.invoice_plan_ids.filtered(lambda l: not l.invoiced)
            if rec.state == "sale" and has_invoice_plan and to_invoice:
                if rec.invoice_status == "to invoice" or (
                    rec.invoice_status == "no"
                    and "advance" in to_invoice.mapped("invoice_type")
                ):
                    rec.ip_invoice_plan = True
                    continue
            rec.ip_invoice_plan = False

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
        prec = Decimal.precision_get("Product Unit of Measure")
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

    def _create_invoices(self, grouped=False, final=False):
        moves = super()._create_invoices(grouped=grouped, final=final)
        invoice_plan_id = self._context.get("invoice_plan_id")
        if invoice_plan_id:
            plan = self.env["sale.invoice.plan"].browse(invoice_plan_id)
            moves.ensure_one()  # Expect 1 invoice for 1 invoice plan
            plan._compute_new_invoice_quantity(moves[0])
            moves.invoice_date = plan.plan_date
            plan.invoice_move_ids += moves
        return moves


class SaleInvoicePlan(models.Model):
    _name = "sale.invoice.plan"
    _description = "Invoice Planning Detail"
    _order = "installment"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sales Order",
        index=True,
        readonly=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="sale_id.partner_id",
        store=True,
        index=True,
    )
    state = fields.Selection(
        [
            ("draft", "Quotation"),
            ("sent", "Quotation Sent"),
            ("sale", "Sales Order"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        related="sale_id.state",
        store=True,
        index=True,
    )
    installment = fields.Integer(string="Installment")
    plan_date = fields.Date(string="Plan Date", required=True)
    invoice_type = fields.Selection(
        [("advance", "Advance"), ("installment", "Installment")],
        string="Type",
        required=True,
        default="installment",
    )
    last = fields.Boolean(
        string="Last Installment",
        compute="_compute_last",
        help="Last installment will create invoice use remaining amount",
    )
    percent = fields.Float(
        string="Percent",
        digits="Product Unit of Measure",
        help="This percent will be used to calculate new quantity",
    )
    invoice_move_ids = fields.Many2many(
        "account.move",
        relation="sale_invoice_plan_invoice_rel",
        column1="plan_id",
        column2="move_id",
        string="Invoices",
        readonly=True,
    )
    to_invoice = fields.Boolean(
        string="Next Invoice",
        compute="_compute_to_invoice",
        help="If this line is ready to create new invoice",
    )
    invoiced = fields.Boolean(
        string="Invoice Created",
        compute="_compute_invoiced",
        help="If this line already invoiced",
    )
    _sql_constraint = [
        (
            "unique_instalment",
            "UNIQUE (sale_id, installment)",
            "Installment must be unique on invoice plan",
        )
    ]

    def _compute_to_invoice(self):
        """ If any invoice is in draft/open/paid do not allow to create inv.
            Only if previous to_invoice is False, it is eligible to_invoice.
        """
        for rec in self:
            rec.to_invoice = False
        for rec in self.sorted("installment"):
            if rec.state != "sale":  # Not confirmed, no to_invoice
                continue
            if not rec.invoiced:
                rec.to_invoice = True
                break

    def _compute_invoiced(self):
        for rec in self:
            invoiced = rec.invoice_move_ids.filtered(
                lambda l: l.state in ("draft", "posted")
            )
            rec.invoiced = invoiced and True or False

    def _compute_last(self):
        for rec in self:
            last = max(rec.sale_id.invoice_plan_ids.mapped("installment"))
            rec.last = rec.installment == last

    def _compute_new_invoice_quantity(self, invoice_move):
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return
        percent = self.percent
        move = invoice_move.with_context({"check_move_validity": False})
        for line in move.invoice_line_ids:
            assert (
                len(line.sale_line_ids) >= 0
            ), "No matched order line for invoice line"
            order_line = fields.first(line.sale_line_ids)
            if order_line.is_downpayment:  # based on 1 unit
                line.write({"quantity": -percent / 100})
            else:
                plan_qty = order_line.product_uom_qty * (percent / 100)
                prec = order_line.product_uom.rounding
                if float_compare(plan_qty, line.quantity, prec) == 1:
                    raise ValidationError(
                        _(
                            "Plan quantity: %s, exceed invoiceable quantity: %s"
                            "\nProduct should be delivered before invoice"
                        )
                        % (plan_qty, line.quantity)
                    )
                line.write({"quantity": plan_qty})
        # Call this method to recompute dr/cr lines
        move._move_autocomplete_invoice_lines_values()
