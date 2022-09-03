from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round


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
    analytic_account_id = fields.Many2one(related="sale_id.analytic_account_id")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="sale_id.partner_id",
        store=True,
        index=True,
    )
    state = fields.Selection(
        string="Status",
        related="sale_id.state",
        store=True,
        index=True,
    )
    installment = fields.Integer()
    plan_date = fields.Date(required=True)
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
        digits="Sales Invoice Plan Percent",
        help="This percent will be used to calculate new quantity",
    )
    amount = fields.Float(
        digits="Product Price",
        compute="_compute_amount",
        inverse="_inverse_amount",
        help="This amount will be used to calculate the percent",
    )
    invoice_move_ids = fields.Many2many(
        "account.move",
        relation="sale_invoice_plan_invoice_rel",
        column1="plan_id",
        column2="move_id",
        string="Invoices",
        readonly=True,
    )
    amount_invoiced = fields.Float(compute="_compute_invoiced")
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
    no_edit = fields.Boolean(
        compute="_compute_no_edit",
    )

    _sql_constraint = [
        (
            "unique_instalment",
            "UNIQUE (sale_id, installment)",
            "Installment must be unique on invoice plan",
        )
    ]

    def _no_edit(self):
        self.ensure_one()
        return self.invoiced

    def _compute_no_edit(self):
        for rec in self:
            rec.no_edit = rec._no_edit()

    @api.depends("percent")
    def _compute_amount(self):
        for rec in self:
            # With invoice already created, no recompute
            if rec.invoiced:
                rec.amount = rec.amount_invoiced
                rec.percent = rec.amount / rec.sale_id.amount_untaxed * 100
                continue
            # For last line, amount is the left over
            if rec.last:
                installments = rec.sale_id.invoice_plan_ids.filtered(
                    lambda l: l.invoice_type == "installment"
                )
                prev_amount = sum((installments - rec).mapped("amount"))
                rec.amount = rec.sale_id.amount_untaxed - prev_amount
                continue
            rec.amount = rec.percent * rec.sale_id.amount_untaxed / 100

    @api.onchange("amount", "percent")
    def _inverse_amount(self):
        for rec in self:
            if rec.sale_id.amount_untaxed != 0:
                if rec.last:
                    installments = rec.sale_id.invoice_plan_ids.filtered(
                        lambda l: l.invoice_type == "installment"
                    )
                    prev_percent = sum((installments - rec).mapped("percent"))
                    rec.percent = 100 - prev_percent
                    continue
                rec.percent = rec.amount / rec.sale_id.amount_untaxed * 100
                continue
            rec.percent = 0

    def _compute_to_invoice(self):
        """If any invoice is in draft/open/paid do not allow to create inv.
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
            rec.amount_invoiced = invoiced[:1].amount_untaxed

    def _compute_last(self):
        for rec in self:
            last = max(rec.sale_id.invoice_plan_ids.mapped("installment"))
            rec.last = rec.installment == last

    def _compute_new_invoice_quantity(self, invoice_move):
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return
        percent = self.percent
        move = invoice_move.with_context(check_move_validity=False)
        for line in move.invoice_line_ids:
            self._update_new_quantity(line, percent)
        move.line_ids.filtered("exclude_from_invoice_tab").unlink()
        move._move_autocomplete_invoice_lines_values()  # recompute dr/cr

    def _update_new_quantity(self, line, percent):
        """Hook function"""
        if not len(line.sale_line_ids) >= 0:
            raise UserError(_("No matched order line for invoice line"))
        order_line = fields.first(line.sale_line_ids)
        if order_line.is_downpayment:  # based on 1 unit
            line.write({"quantity": -percent / 100})
        else:
            plan_qty = self._get_plan_qty(order_line, percent)
            prec = order_line.product_uom.rounding
            if plan_qty:
                plan_qty = float_round(plan_qty, precision_rounding=prec)
            if float_compare(abs(plan_qty), abs(line.quantity), prec) == 1:
                raise ValidationError(
                    _(
                        "Plan quantity: %(plan_qty)s, exceed invoiceable quantity: "
                        "%(invoiceable_qty)s"
                        "\nProduct should be delivered before invoice"
                    )
                    % {"plan_qty": plan_qty, "invoiceable_qty": line.quantity}
                )
            line.write({"quantity": plan_qty})

    @api.model
    def _get_plan_qty(self, order_line, percent):
        plan_qty = order_line.product_uom_qty * (percent / 100)
        return plan_qty

    def unlink(self):
        lines = self.filtered("no_edit")
        if lines:
            installments = [str(x) for x in lines.mapped("installment")]
            raise UserError(
                _(
                    "Installment %s: already used and not allowed to delete.\n"
                    "Please discard changes."
                )
                % ", ".join(installments)
            )
        return super().unlink()
