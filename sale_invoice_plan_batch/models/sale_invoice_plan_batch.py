# Copyright 2024 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleInvoicePlanBatch(models.Model):
    _name = "sale.invoice.plan.batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Create invoices from invoice plan in batch"
    _check_company_auto = True
    _order = "id desc"

    name = fields.Char(
        required=True,
        readonly=True,
        default=lambda self: _("New"),
        copy=False,
    )
    description = fields.Char(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        readonly=True,
        default=lambda self: self.env.company,
    )
    batch_line_ids = fields.One2many(
        comodel_name="sale.invoice.plan.batch.line",
        inverse_name="batch_id",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "ready": [("readonly", False)],
        },
        help="Selected invoice plan to create invoice",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("done", "Done"),
            ("done_exception", "Done with Exception"),
        ],
        default="draft",
        tracking=True,
        index=True,
        required=True,
        readonly=True,
    )
    # Filters
    plan_date_from = fields.Date(
        string="Plan Date From",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="All un-invoiced invoice plan with plan date prior to this date will be included",
    )
    plan_date_to = fields.Date(
        string="Plan Date To",
        default=fields.Date.today,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="All un-invoiced invoice plan with plan date prior to this date will be included",
    )
    sale_ids = fields.Many2many(
        comodel_name="sale.order",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", "Batch name must be unique!"),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "sale.invoice.plan.batch"
                ) or _("New")
        return super().create(vals_list)

    def reset_to_draft(self):
        self.write({"state": "draft"})

    def _get_filter(self):
        self.ensure_one()
        domain = [
            ("invoice_type", "=", "installment"),
            ("state", "in", ("sale", "done")),
            ("invoiced", "=", False),
            ("plan_date", "<=", self.plan_date_to),
            ("sale_id.invoice_status", "=", "to invoice"),
        ]
        if self.plan_date_from:
            domain.append(("plan_date", ">=", self.plan_date_from))
        if self.partner_ids:
            domain.append(("partner_id", "in", self.partner_ids.ids))
        if self.sale_ids:
            domain.append(("sale_id", "in", self.sale_ids.ids))
        return domain

    def get_planned_installments(self):
        for batch in self:
            domain = batch._get_filter()
            installments = self.env["sale.invoice.plan"].search(
                domain, order="sale_id desc, installment"
            )
            batch.batch_line_ids.unlink()
            lines = [(0, 0, {"invoice_plan_id": x.id}) for x in installments]
            batch.write({"batch_line_ids": lines})
        self.write({"state": "ready"})

    def create_invoices(self):
        batch_lines = self.mapped("batch_line_ids")
        if not batch_lines:
            raise ValidationError(_("No installment to process!"))
        MakeInvoice = self.env["sale.advance.payment.inv"]
        sales = batch_lines.mapped("invoice_plan_id.sale_id")
        for sale in sales:  # Process by sale order group
            sale_batch_lines = batch_lines.filtered(lambda l: l.sale_id == sale)
            MakeInvoice = MakeInvoice.with_context(
                active_ids=[sale.id]
            )  # on a sale doc
            for bl in sale_batch_lines.sorted("installment"):
                if bl.invoiced or bl.error:
                    continue
                try:  # simulate make invoice wizard
                    makeinv_wizard = {"advance_payment_method": "delivered"}
                    makeinvoice = MakeInvoice.create(makeinv_wizard)
                    makeinvoice.sudo().with_context(
                        invoice_plan_id=bl.invoice_plan_id.id
                    ).create_invoices()
                    self.env.cr.commit()
                except Exception as e:
                    bl.error = True
                    bl.error_message = e
        self.write({"state": "done"})

    def open_sales(self):
        self.ensure_one()
        action = {
            "name": _("Sales Order"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "list,form",
            "domain": [("id", "in", self.batch_line_ids.sale_id.ids)],
            "context": {"create": False},
        }
        return action

    def open_invoices(self):
        self.ensure_one()
        action = {
            "name": _("Customer Invoices"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", self.batch_line_ids.invoice_move_ids.ids)],
            "context": {"create": False},
        }
        return action

    def unlink(self):
        recs = self.filtered(lambda l: l.state in ["done", "done_exception"])
        if recs:
            raise ValidationError(
                _("The batch %s is not in draft state, so you cannot delete it.")
                % ", ".join(recs.mapped("name"))
            )
        return super().unlink()


class SaleInvoicePlanBatchLine(models.Model):
    _name = "sale.invoice.plan.batch.line"
    _description = "Sale Invoice Plan Batch Line"
    _order = "id"

    batch_id = fields.Many2one(comodel_name="sale.invoice.plan.batch", index=True)
    invoice_plan_id = fields.Many2one(
        comodel_name="sale.invoice.plan",
        readonly=True,
    )
    sale_id = fields.Many2one(
        related="invoice_plan_id.sale_id",
    )
    partner_id = fields.Many2one(
        related="sale_id.partner_id",
    )
    installment = fields.Integer(
        related="invoice_plan_id.installment",
    )
    plan_date = fields.Date(
        related="invoice_plan_id.plan_date",
    )
    invoice_type = fields.Selection(
        related="invoice_plan_id.invoice_type",
    )
    percent = fields.Float(
        related="invoice_plan_id.percent",
    )
    amount = fields.Float(
        related="invoice_plan_id.amount",
    )
    invoiced = fields.Boolean(
        related="invoice_plan_id.invoiced",
    )
    invoice_move_ids = fields.Many2many(
        comodel_name="account.move",
        related="invoice_plan_id.invoice_move_ids",
    )
    error = fields.Boolean()
    error_message = fields.Text()
