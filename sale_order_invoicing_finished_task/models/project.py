# Copyright 2017 Camptocamp SA
# Copyright 2017 Tecnativa - Sergio Teruel
# Copyright 2017 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    invoiceable = fields.Boolean()


class ProjectTask(models.Model):
    _inherit = "project.task"

    invoiceable = fields.Boolean()
    invoicing_finished_task = fields.Boolean(
        related="sale_line_id.product_id.invoicing_finished_task",
    )

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        tasks = self.filtered(
            lambda t: (
                t.invoicing_finished_task
                and t.stage_id.invoiceable
                and not t.invoiceable
            )
        )
        tasks.toggle_invoiceable()

    def toggle_invoiceable(self):
        self._check_sale_line_state()
        for task in self:
            task.invoiceable = not task.invoiceable

    def write(self, vals):
        if "sale_line_id" in vals:
            self._check_sale_line_state(vals["sale_line_id"])
        res = super().write(vals)
        if "invoiceable" in vals:
            self.mapped("sale_line_id")._compute_qty_delivered()
        return res

    @api.model
    def create(self, vals):
        if "sale_line_id" in vals:
            self._check_sale_line_state(vals["sale_line_id"])
        return super().create(vals)

    def _check_sale_line_state(self, sale_line_id=False):
        sale_lines = self.mapped("sale_line_id")
        if sale_line_id:
            sale_lines |= self.env["sale.order.line"].browse(sale_line_id)
        for sale_line in sale_lines:
            if (
                sale_line.state in ("done", "cancel")
                or sale_line.invoice_status == "invoiced"
            ):
                raise ValidationError(
                    _(
                        "You cannot create/modify a task related with a "
                        "invoiced, done or cancel sale order line "
                    )
                )
