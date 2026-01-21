# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    force_invoice = fields.Boolean()
    force_invoice_order_filter_domain = fields.Text(
        string="Force Invoice Order Filter Domain",
        related="force_invoice_order_filter_id.domain",
    )
    force_invoice_order_filter_id = fields.Many2one(
        comodel_name="ir.filters",
        default=lambda self: self._default_filter(
            "sale_automatic_workflow_force_invoice.automatic_workflow_force_invoice_filter"
        ),
    )

    @api.constrains(
        "force_invoice", "create_invoice", "validate_invoice", "register_payment"
    )
    def _check_force_invoice(self):
        for record in self.filtered("force_invoice"):
            incompatible = []
            if record.create_invoice:
                incompatible.append(_("Create Invoice"))
            if record.validate_invoice:
                incompatible.append(_("Validate Invoice"))
            if record.register_payment:
                incompatible.append(_("Register Payment"))
            if incompatible:
                raise ValidationError(
                    _("Force invoice option is not compatible with: %s")
                    % ", ".join(incompatible)
                )
