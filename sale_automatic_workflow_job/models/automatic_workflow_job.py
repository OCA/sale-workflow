# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models

from odoo.addons.queue_job.job import identity_exact


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _do_validate_sale_order_job_options(self, sale, domain_filter):
        description = _("Validate sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _validate_sale_orders(self, domain_filter):
        with_context = self.with_context(auto_delay_do_validation=True)
        return super(AutomaticWorkflowJob, with_context)._validate_sale_orders(
            domain_filter
        )

    def _do_create_invoice_job_options(self, sale, domain_filter):
        description = _("Create invoices for sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _create_invoices(self, domain_filter):
        with_context = self.with_context(auto_delay_do_create_invoice=True)
        return super(AutomaticWorkflowJob, with_context)._create_invoices(domain_filter)

    def _do_validate_invoice_job_options(self, invoice, domain_filter):
        description = _("Validate invoice {}").format(invoice.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _validate_invoices(self, domain_filter):
        with_context = self.with_context(auto_delay_do_validation=True)
        return super(AutomaticWorkflowJob, with_context)._validate_invoices(
            domain_filter
        )

    def _do_validate_picking_job_options(self, picking, domain_filter):
        description = _("Validate transfer {}").format(picking.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _validate_pickings(self, domain_filter):
        with_context = self.with_context(auto_delay_do_validation=True)
        return super(AutomaticWorkflowJob, with_context)._validate_pickings(
            domain_filter
        )

    def _do_sale_done_job_options(self, sale, domain_filter):
        description = _("Mark sales order {} as done").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _sale_done(self, domain_filter):
        with_context = self.with_context(auto_delay_do_sale_done=True)
        return super(AutomaticWorkflowJob, with_context)._sale_done(domain_filter)

    def _register_hook(self):
        mapping = {
            "_do_validate_sale_order": "auto_delay_do_validation",
            "_do_create_invoice": "auto_delay_do_create_invoice",
            "_do_validate_invoice": "auto_delay_do_validation",
            "_do_validate_picking": "auto_delay_do_validation",
            "_do_sale_done": "auto_delay_do_sale_done",
        }
        for method_name, context_key in mapping.items():
            self._patch_method(
                method_name,
                self._patch_job_auto_delay(method_name, context_key=context_key),
            )
        return super()._register_hook()
