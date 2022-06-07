# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.sale_automatic_workflow.models.automatic_workflow_job import savepoint


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    @api.model
    def run_with_workflow(self, sale_workflow):
        workflow_domain = [("workflow_process_id", "=", sale_workflow.id)]
        if sale_workflow.automated_advance_payment_create:
            self._automated_advance_payment_create(
                safe_eval(sale_workflow.advance_payment_filter_id.domain)
                + workflow_domain
            )
        return super(AutomaticWorkflowJob, self).run_with_workflow(
            sale_workflow=sale_workflow
        )

    @api.model
    def _automated_advance_payment_create(self, order_filter):
        sales = self.env["sale.order"].search(order_filter)
        for sale in sales:
            with savepoint(self.env.cr):
                self._do_automated_advance_payment_create(
                    sale.with_company(sale.company_id), order_filter
                )

    def _do_automated_advance_payment_create(self, sale, domain_filter):
        if not self.env["sale.order"].search_count(
            [("id", "=", sale.id)] + domain_filter
        ):
            return "{} {} job bypassed".format(sale.display_name, sale)
        else:
            ctx = {
                "active_ids": sale.ids,
                "default_order_id": sale.id,
                "default_amount_total": sale.amount_residual,
                "default_currency_id": sale.pricelist_id.currency_id.id,
            }
            bank_journal = (
                self.env["account.journal"]
                .search(
                    [
                        ("type", "=", "bank"),
                        ("company_id", "=", self.env.company.id),
                    ],
                    limit=1,
                )
                .id,
            )
            self.env["account.voucher.wizard"].with_context(**ctx).create(
                {
                    "journal_id": bank_journal,
                    "amount_advance": sale.amount_residual,
                }
            ).make_advance_payment()
            return "{} {} advance payment successfully".format(sale.display_name, sale)
