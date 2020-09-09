# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools

from odoo import _, models

from odoo.addons.queue_job.job import identity_exact, job, related_action


# TODO integrate in queue_job
def job_auto_delay(func=None, default_channel="root", retry_pattern=None):
    """Decorator to automatically delay as job method when called

    The decorator applies ``odoo.addons.queue_job.job`` at the same time,
    so the decorated method is listed in job functions. The arguments
    are the same, propagated to the ``job`` decorator.

    When a method is decorated by ``job_auto_delay``, any call to the method
    will not directly execute the method's body, but will instead enqueue a
    job.

    The options of the job usually passed to ``with_delay()`` (priority,
    description, identity_key, ...) can be returned in a dictionary by a method
    named after the name of the method suffixed by ``_job_options`` which takes
    the same parameters as the initial method.

    It is still possible to directly execute the method by setting a key
    ``_job_force_sync`` to True in the environment context.

    Example:

    .. code-block:: python

        class ProductProduct(models.Model):
            _inherit = 'product.product'

            def foo_job_options(self, arg1):
                return {
                  "priority": 100,
                  "description": "Saying hello to {}".format(arg1)
                }

            @job_auto_delay(default_channel="root.channel1")
            def foo(self, arg1):
                print("hello", arg1)

            def button_x(self):
                foo("world")

    The result when ``button_x`` is called, is that a new job for ``foo`` is
    delayed.

    """
    if func is None:
        return functools.partial(
            job_auto_delay, default_channel=default_channel, retry_pattern=retry_pattern
        )

    def auto_delay(self, *args, **kwargs):
        if self.env.context.get("job_uuid") or self.env.context.get("_job_force_sync"):
            # we are in the job execution
            return func(self, *args, **kwargs)
        else:
            # replace the synchronous call by a job on itself
            method_name = func.__name__
            job_options_method = getattr(
                self, "{}_job_options".format(method_name), None
            )
            job_options = {}
            if job_options_method:
                job_options.update(job_options_method(*args, **kwargs))
            else:
                job_options = {}
            delayed = self.with_delay(**job_options)
            getattr(delayed, method_name)(*args, **kwargs)

    return functools.update_wrapper(
        auto_delay,
        job(func, default_channel=default_channel, retry_pattern=retry_pattern),
    )


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _validate_sale_orders_job_options(self, order_filter):
        description = _("Validate sales order:")
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _validate_sale_orders(self, order_filter):
        sales = super()._validate_sale_orders(order_filter)
        self._update_job_name(sales)
        return self._get_result_dict(sales)

    def _create_invoices_job_options(self, create_filter):
        description = _("Create invoices for sales order:")
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _create_invoices(self, create_filter):
        sales = super()._create_invoices(create_filter)
        self._update_job_name(sales)
        return self._get_result_dict(sales)

    def _validate_invoices_job_options(self, validate_invoice_filter):
        description = _("Validate invoice:")
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _validate_invoices(self, validate_invoice_filter):
        invoices = super()._validate_invoices(validate_invoice_filter)
        self._update_job_name(invoices)
        return self._get_result_dict(invoices)

    def _validate_pickings_job_options(self, picking_filter):
        description = _("Validate transfer:")
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _validate_pickings(self, picking_filter):
        pickings = super()._validate_pickings(picking_filter)
        self._update_job_name(pickings)
        return self._get_result_dict(pickings)

    def _sale_done_job_options(self, sale_done_filter):
        description = _("Sale orders mark as done:")
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    @related_action("_related_action_sale_automatic_workflow")
    def _sale_done(self, sale_done_filter):
        sales = super()._sale_done(sale_done_filter)
        self._update_job_name(sales)
        return self._get_result_dict(sales)

    def _get_result_dict(self, obj):
        result = {"ids": obj.ids, "model": obj._name} if obj else {}
        return result

    def _update_job_name(self, obj):
        uuid = self._context.get("job_uuid", False)
        job = self.env["queue.job"].search([("uuid", "=", uuid)], limit=1)
        new_name = _("{} {}").format(
            job.name, ", ".join(obj and obj.mapped("display_name") or [])
        )
        job.write({"name": new_name})
        return job
