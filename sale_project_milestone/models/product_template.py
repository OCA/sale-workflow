# Copyright 2025 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_tracking = fields.Selection(
        selection_add=[
            ("milestone_project", "Project & Milestone"),
        ],
        ondelete={"milestone_project": "set default"},
    )

    @api.depends("service_tracking", "service_policy", "type")
    def _compute_product_tooltip(self):
        res = super()._compute_product_tooltip()
        for record in self.filtered(lambda r: r.type == "service"):
            if record.service_tracking == "milestone_project":
                if record.service_policy == "delivered_milestones":
                    record.product_tooltip = _(
                        "Invoice your milestones when they are reached. "
                        "Create a project (or select an existing one) "
                        "with a milestone for the order."
                    )
                elif record.service_policy == "ordered_prepaid":
                    record.product_tooltip = _(
                        "Invoice ordered quantities as soon as this service is sold. "
                        "Create a project (or select an existing one) "
                        "with a milestone for the order."
                    )
                elif record.service_policy == "delivered_manual":
                    record.product_tooltip = _(
                        "Invoice this service when it is delivered (set the quantity by hand). "
                        "Create a project (or select an existing one) "
                        "with a milestone for the order."
                    )
        return res

    @api.constrains("project_id", "project_template_id", "service_tracking")
    def _check_project_and_template(self):
        """Extend constraints for milestone_project tracking."""
        res = super()._check_project_and_template()
        for product in self:
            if product.service_tracking == "milestone_project" and product.project_id:
                raise ValidationError(
                    _(
                        "The product %(product)s should not have a global project "
                        "since it will generate a project."
                    )
                    % {"product": product.name}
                )
        return res

    @api.onchange("service_tracking")
    def _onchange_service_tracking(self):
        res = super()._onchange_service_tracking()
        if self.service_tracking == "milestone_project":
            self.project_id = False
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("service_tracking")
    def _onchange_service_tracking(self):
        res = super()._onchange_service_tracking()
        if self.service_tracking == "milestone_project":
            self.project_id = False
        return res
