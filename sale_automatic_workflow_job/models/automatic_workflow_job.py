# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import functools
import logging

from odoo import api, models

from odoo.addons.queue_job.job import Job, identity_exact
from odoo.addons.queue_job.utils import must_run_without_delay

_logger = logging.getLogger(__name__)


def _skip_on_failed_job(patched, method_name, context_key):
    def wrapper(self, *args, **kwargs):
        if (
            self.env.context.get(context_key)
            and not self.env.context.get("job_uuid")
            and not must_run_without_delay(self.env)
            and self._has_failed_job(method_name, *args, **kwargs)
        ):
            _logger.info(
                "%s not enqueued: the same job failed and waits to be requeued",
                method_name,
            )
            return None
        return patched(self, *args, **kwargs)

    return wrapper


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
        description = self.env._("Validate sales order %s", sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _do_send_order_confirmation_mail_job_options(self, sale):
        description = self.env._("Send order %s confirmation mail", sale.display_name)
        return {"description": description, "identity_key": identity_exact}

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

    def _do_send_order_confirmation_mail(self, sale):
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
        description = self.env._(
            "Create invoices for sales order %s", sale.display_name
        )
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _create_invoices(self, domain_filter):
        with_context = self.with_context(auto_delay_do_create_invoice=True)
        return super(AutomaticWorkflowJob, with_context)._create_invoices(domain_filter)

    def _do_validate_invoice_job_options(self, invoice, domain_filter):
        description = self.env._("Validate invoice %s", invoice.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _validate_invoices(self, domain_filter):
        with_context = self.with_context(auto_delay_do_validation=True)
        return super(AutomaticWorkflowJob, with_context)._validate_invoices(
            domain_filter
        )

    def _do_sale_done_job_options(self, sale, domain_filter):
        description = self.env._("Mark sales order %s as done", sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _sale_done(self, domain_filter):
        with_context = self.with_context(auto_delay_do_sale_done=True)
        return super(AutomaticWorkflowJob, with_context)._sale_done(domain_filter)

    def _register_hook(self):
        mapping = self._get_register_hook_mapping()
        for method_name, context_key in mapping.items():
            origin = getattr(type(self), method_name)
            patched = self._patch_job_auto_delay(method_name, context_key=context_key)
            setattr(
                type(self),
                method_name,
                functools.update_wrapper(
                    _skip_on_failed_job(patched, method_name, context_key),
                    origin,
                ),
            )

        return super()._register_hook()

    def _has_failed_job(self, method_name, *args, **kwargs):
        options_method = getattr(self, f"{method_name}_job_options", None)
        identity_key = options_method and options_method(*args, **kwargs).get(
            "identity_key"
        )
        if not identity_key:
            return False
        job = Job(
            getattr(self, method_name),
            args=args,
            kwargs=kwargs,
            identity_key=identity_key,
        )
        return bool(
            self.env["queue.job"]
            .sudo()
            .search_count(
                [("identity_key", "=", job.identity_key), ("state", "=", "failed")],
                limit=1,
            )
        )

    def _get_register_hook_mapping(self) -> dict[str, str]:
        return {
            "_do_validate_sale_order": "auto_delay_do_validation",
            "_do_send_order_confirmation_mail": "auto_delay_do_send_mail",
            "_do_create_invoice": "auto_delay_do_create_invoice",
            "_do_validate_invoice": "auto_delay_do_validation",
            "_do_sale_done": "auto_delay_do_sale_done",
        }
