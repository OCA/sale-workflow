# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleCreateOrderPlan(models.TransientModel):
    _name = "sale.create.order.plan"
    _description = "Filling order planning criteria"

    num_installment = fields.Integer(
        string="Number of Installment",
        default=2,
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

    def sale_create_order_plan(self):
        sale = self.env["sale.blanket.order"].browse(self._context.get("active_id"))
        self.ensure_one()
        sale.create_order_plan(
            self.num_installment,
            self.installment_date,
            self.interval,
            self.interval_type,
        )
        return {"type": "ir.actions.act_window_close"}
