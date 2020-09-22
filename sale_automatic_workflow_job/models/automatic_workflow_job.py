# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models

from odoo.addons.queue_job.job import identity_exact, job_auto_delay, related_action


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _do_validate_sale_order_job_options(self, sale, domain_filter):
        description = _("Validate sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _do_validate_sale_order(self, sale, domain_filter):
        return super()._do_validate_sale_order(sale, domain_filter)

    def _do_create_invoice_job_options(self, sale, domain_filter):
        description = _("Create invoices for sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _do_create_invoice(self, sale, domain_filter):
        return super()._do_create_invoice(sale, domain_filter)

    def _do_validate_invoice_job_options(self, invoice, domain_filter):
        description = _("Validate invoice {}").format(invoice.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _do_validate_invoice(self, invoice, domain_filter):
        return super()._do_validate_invoice(invoice, domain_filter)

    def _do_validate_picking_job_options(self, picking, domain_filter):
        description = _("Validate transfer {}").format(picking.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _do_validate_picking(self, picking, domain_filter):
        return super()._do_validate_picking(picking, domain_filter)

    def _do_sale_done_job_options(self, sale, domain_filter):
        description = _("Mark sales order {} as done").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _do_sale_done(self, sale, domain_filter):
        return super()._do_sale_done(sale, domain_filter)
