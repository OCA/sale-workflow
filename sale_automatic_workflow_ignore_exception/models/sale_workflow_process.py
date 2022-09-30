# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleWorkflowProcess(models.Model):

    _inherit = "sale.workflow.process"

    ignore_exception_when_confirm = fields.Boolean()
