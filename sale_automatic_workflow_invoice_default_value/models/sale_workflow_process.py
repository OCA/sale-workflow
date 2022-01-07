# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleWorkflowProcess(models.Model):

    _inherit = "sale.workflow.process"

    create_invoice_default_value_ids = fields.One2many(
        comodel_name="automatic.workflow.invoice.default.value",
        inverse_name="process_id",
        string="Create Invoice Default values",
        copy=True,
    )
