# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    auto_assign = fields.Boolean(
        string="Auto assign",
        help=(
            "When enabled the workflow will be assigned at sales order creation, "
            "if the assignation domain below applies."
        ),
    )
    auto_assign_domain = fields.Text(string="Auto assign domain")
    auto_assign_priority = fields.Integer(
        default=10,
        help=(
            "Determines the priority of the workflow when auto-assigning. "
            "Lower numbers have higher priority."
        ),
    )
