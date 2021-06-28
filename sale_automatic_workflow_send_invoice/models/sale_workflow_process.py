# Copyright (C) 2021 Manuel Calero <manuelcalero@xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"
    _description = "Sale Workflow Process"

    send_invoice = fields.Boolean()
    send_invoice_filter_domain = fields.Text(
        string="Send Invoice Filter Domain", related="send_invoice_filter_id.domain",
    )
    send_invoice_filter_id = fields.Many2one(
        "ir.filters",
        string="Send Invoice Filter",
        default=lambda self: self._default_filter(
            "sale_automatic_workflow_send_invoice."
            "automatic_workflow_send_invoice_filter"
        ),
    )
