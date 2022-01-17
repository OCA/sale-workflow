# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AutomaticWorkflowJob(models.Model):

    _inherit = "automatic.workflow.job"

    def _do_validate_sale_order(self, sale, domain_filter):
        if sale.workflow_process_id.ignore_exception_when_confirm:
            sale = sale.with_context(ignore_exception_when_confirm=True)
        return super()._do_validate_sale_order(sale, domain_filter)
