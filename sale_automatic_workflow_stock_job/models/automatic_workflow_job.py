# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.queue_job.job import identity_exact


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    def _do_validate_picking_job_options(self, picking, domain_filter):
        description = self.env._("Validate transfer %s", picking.display_name)
        return {
            "description": description,
            "identity_key": identity_exact,
        }

    def _validate_pickings(self, picking_filter):
        with_context = self.with_context(auto_delay_do_validation=True)
        return super(AutomaticWorkflowJob, with_context)._validate_pickings(
            picking_filter
        )

    def _register_hook(self):
        self._patch_method(
            "_do_validate_picking",
            self._patch_job_auto_delay(
                "_do_validate_picking", context_key="auto_delay_do_validation"
            ),
        )
        return super()._register_hook()
