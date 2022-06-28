from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


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

    def _compute_last(self):
        for rec in self:
            last = max(rec.sale_id.invoice_plan_ids.mapped("installment"))
            rec.last = rec.installment == last

    def _compute_new_invoice_quantity(self, invoice_move):
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return
        percent = self.percent
        move = invoice_move.with_context(**{"check_move_validity": False})
        for line in move.invoice_line_ids:
            if not len(line.sale_line_ids) >= 0:
                raise UserError(_("No matched order line for invoice line"))
            order_line = fields.first(line.sale_line_ids)
            if order_line.is_downpayment:  # based on 1 unit
                line.write({"quantity": -percent / 100})
            else:
                plan_qty = order_line.product_uom_qty * (percent / 100)
                prec = order_line.product_uom.rounding
                if float_compare(plan_qty, line.quantity, prec) == 1:
                    raise ValidationError(
                        _(
                            "Plan quantity: %(plan_qty)s, exceed invoiceable quantity: "
                            "%(invoiceable_qty)s"
                            "\nProduct should be delivered before invoice"
                        )
                        % {"plan_qty": plan_qty, "invoiceable_qty": line.quantity}
                    )
                line.write({"quantity": plan_qty})
        # Call this method to recompute dr/cr lines
        move.line_ids.filtered("exclude_from_invoice_tab").unlink()
        move._move_autocomplete_invoice_lines_values()
