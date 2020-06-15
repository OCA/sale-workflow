# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools

from odoo import _, models
from odoo.addons.queue_job.job import job, identity_exact


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
            job_auto_delay,
            default_channel=default_channel,
            retry_pattern=retry_pattern
        )

    def auto_delay(self, *args, **kwargs):
        if (self.env.context.get("job_uuid") or
                self.env.context.get("_job_force_sync")):
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
        job(
            func,
            default_channel=default_channel,
            retry_pattern=retry_pattern
        ),
    )


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _do_validate_sale_order_job_options(self, sale):
        description = _("Validate sales order {}").format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    def _do_validate_sale_order(self, sale):
        return super()._do_validate_sale_order(sale)

    def _do_create_invoice_job_options(self, sale):
        description = _(
            "Create invoices for sales order {}"
        ).format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    def _do_create_invoice(self, sale):
        return super()._do_create_invoice(sale)

    def _do_validate_invoice_job_options(self, invoice):
        description = _("Validate invoice {}").format(invoice.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    def _do_validate_invoice(self, invoice):
        return super()._do_validate_invoice(invoice)

    def _do_validate_picking_job_options(self, picking):
        description = _("Validate transfer {}").format(picking.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    def _do_validate_picking(self, picking):
        return super()._do_validate_picking(picking)

    def _do_sale_done_job_options(self, sale):
        description = _(
            "Mark sales order {} as done"
        ).format(sale.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    @job_auto_delay(default_channel="root.auto_workflow")
    def _do_sale_done(self, sale):
        return super()._do_sale_done(sale)
