# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleCreateInvoicePlan(models.TransientModel):
    _name = "sale.create.invoice.plan"
    _description = "Fillig invoice planning criteria"

    advance = fields.Boolean(
        string="Advance on 1st Invoice",
        default=False,
    )
    num_installment = fields.Integer(
        string="Number of Installment",
        default=0,
        required=True,
    )
    installment_date = fields.Date(
        default=fields.Date.context_today,
        required=True,
    )
    interval = fields.Integer(
        default=1,
        required=True,
    )
    interval_type = fields.Selection(
        [("day", "Day"), ("month", "Month"), ("year", "Year")],
        default="month",
        required=True,
    )

    @api.constrains("num_installment")
    def _check_num_installment(self):
        for rec in self:
            if rec.num_installment <= 1:
                raise ValidationError(_("Number Installment must greater than 1"))

    def sale_create_invoice_plan(self):
        sale = self.env["sale.order"].browse(self._context.get("active_id"))
        self.ensure_one()
        sale.create_invoice_plan(
            self.num_installment,
            self.installment_date,
            self.interval,
            self.interval_type,
            self.advance,
        )
        return {"type": "ir.actions.act_window_close"}
