# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, models

from odoo.addons.queue_job.job import identity_exact


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _do_validate_sale_order_job_options(self, sale):
        description = _("Validate sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _register_hook(self):
        self._patch_method(
            "_do_validate_sale_order",
            self._patch_job_auto_delay(
                "_do_validate_sale_order", context_key="auto_delay_validate_sale_orders"
            ),
        )
        self._patch_method(
            "_do_create_invoice",
            self._patch_job_auto_delay(
                "_do_create_invoice", context_key="auto_delay_create_invoices"
            ),
        )
        self._patch_method(
            "_do_validate_invoice",
            self._patch_job_auto_delay(
                "_do_validate_invoice", context_key="auto_delay_validate_invoices"
            ),
        )
        self._patch_method(
            "_do_validate_picking",
            self._patch_job_auto_delay(
                "_do_validate_picking", context_key="auto_delay_validate_pickings"
            ),
        )
        self._patch_method(
            "_do_sale_done",
            self._patch_job_auto_delay(
                "_do_sale_done", context_key="auto_delay_sale_done"
            ),
        )
        return super()._register_hook()

    def _validate_sale_orders(self, sale):
        return super(
            AutomaticWorkflowJob, self.with_context(auto_delay_ddmrp_cron_actions=True)
        )._validate_sale_orders(sale)

    def _do_create_invoice_job_options(self, sale):
        description = _("Create invoices for sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _create_invoices(self, sale):
        return super(
            AutomaticWorkflowJob, self.with_context(auto_delay_create_invoices=True)
        )._create_invoices(sale)

    def _do_validate_invoice_job_options(self, invoice):
        description = _("Validate invoice {}").format(invoice.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _validate_invoices(self, invoice):
        return super(
            AutomaticWorkflowJob, self.with_context(auto_delay_validate_invoices=True)
        )._validate_invoices(invoice)

    def _do_validate_picking_job_options(self, picking):
        description = _("Validate transfer {}").format(picking.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _validate_pickings(self, picking):
        return super(
            AutomaticWorkflowJob, self.with_context(auto_delay_validate_pickings=True)
        )._validate_pickings(picking)

    def _do_sale_done_job_options(self, sale):
        description = _("Mark sales order {} as done").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _sale_done(self, sale):
        return super(
            AutomaticWorkflowJob, self.with_context(auto_delay_sale_done=True)
        )._sale_done(sale)
