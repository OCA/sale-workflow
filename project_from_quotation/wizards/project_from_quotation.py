# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProjectFromQuotation(models.TransientModel):
    _name = "project.from.quotation"
    _description = "Project from Quotation"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        required=True,
    )
    mode = fields.Selection(
        selection=[
            ("project", "Create a project"),
            ("tasks_per_line", "Create a project with task per line"),
            ("tasks_per_product", "Create a project with task per product"),
        ],
        required=True,
    )
    order_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        compute="_compute_order_line_ids",
        domain="[('order_id', '=', sale_order_id)]",
        readonly=False,
        store=True,
    )

    @api.depends("sale_order_id")
    def _compute_order_line_ids(self):
        for r in self:
            if r.sale_order_id:
                r.order_line_ids = r.sale_order_id.order_line.filtered(
                    lambda l: not self.env["project.task"].search_count(
                        [
                            ("quotation_line_id", "=", l.id),
                        ]
                    )
                ).ids
            else:
                r.order_line_ids = False

    def action_create_project(self):
        self.ensure_one()
        project = self.sale_order_id._create_project_from_quotation(
            order_lines=self.order_line_ids,
            mode=self.mode,
        )
        return project
