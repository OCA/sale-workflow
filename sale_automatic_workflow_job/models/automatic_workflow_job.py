# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models

from odoo.addons.queue_job.job import identity_exact


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    @api.model
    def _job_prepare_context_before_enqueue_keys(self):
        res = super()._job_prepare_context_before_enqueue_keys()
        res += (
            "send_order_confirmation_mail_in_job",
            "auto_delay_do_send_mail",
            "auto_delay_do_validation_finished",
        )
        return res

    def _do_validate_sale_order_job_options(self, sale, domain_filter):
        description = _("Validate sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _do_validate_sale_order(self, sale, domain_filter):
        send_order_confirmation_mail = self.env.context.get(
            "send_order_confirmation_mail_in_job", False
        )
        result = super()._do_validate_sale_order(sale, domain_filter)
        if send_order_confirmation_mail:
            self.with_context(
                auto_delay_do_validation_finished=True,
                # if we don't clear job_uuid, then a new job will not be created
                job_uuid=False,
            )._do_send_order_confirmation_mail(sale)
        return result

    def _do_send_order_confirmation_mail_job_options(self, sale):
        description = _("Send order {} confirmation mail").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _do_send_order_confirmation_mail(self, sale):
        # Deliberate no-op unless the order has just been confirmed inside the
        # validation job: the guard prevents the synchronous cron path from
        # sending the mail before the queued confirmation runs. Do not remove.
        if self.env.context.get("auto_delay_do_validation_finished"):
            return super()._do_send_order_confirmation_mail(sale)

    def _validate_sale_orders(self, domain_filter):
        with_context = self.with_context(
            auto_delay_do_validation=True,
            auto_delay_do_send_mail=True,
            auto_delay_do_validation_finished=False,
            send_order_confirmation_mail_in_job=self.env.context.get(
                "send_order_confirmation_mail", False
            ),
            send_order_confirmation_mail=False,
        )
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
            "_do_send_order_confirmation_mail": "auto_delay_do_send_mail",
        }
        for method_name, context_key in mapping.items():
            self._patch_method(
                method_name,
                self._patch_job_auto_delay(method_name, context_key=context_key),
            )
        return super()._register_hook()
