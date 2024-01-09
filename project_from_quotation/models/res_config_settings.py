# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_project_from_quotation = fields.Boolean(
        string="Create Projects From Quotations",
        implied_group="project_from_quotation.group_project_from_quotation",
    )
    quotation_template_task_id = fields.Many2one(
        comodel_name="project.task",
        string="Template Task",
        domain=[("active", "in", [True, False])],
        config_parameter="project_from_quotation.template_task_id",
    )
    quotation_template_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Template Project",
        domain=[("active", "in", [True, False])],
        config_parameter="project_from_quotation.template_project_id",
    )
