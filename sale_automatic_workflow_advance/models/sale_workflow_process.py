# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    @api.model
    def _default_journal(self):
        return self.env["account.journal"].search(
            [
                ("type", "in", ("bank", "cash")),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )

    automated_advance_payment_create = fields.Boolean()
    advance_payment_filter_id = fields.Many2one(
        "ir.filters",
        default=lambda self: self._default_filter(
            "sale_automatic_workflow_advance.automatic_workflow_advance_payment_filter"
        ),
    )
    advance_payment_filter_domain = fields.Text(
        string="Advance Payment Filter Domain",
        related="advance_payment_filter_id.domain",
    )
    bank_journal_id = fields.Many2one(
        "account.journal",
        domain="[('type', 'in', ('bank', 'cash'))]",
        default=_default_journal,
        check_company=True,
    )
