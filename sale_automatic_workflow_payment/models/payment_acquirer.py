# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    workflow_process_id = fields.Many2one(
        comodel_name="sale.workflow.process", string="Automatic Workflow"
    )
