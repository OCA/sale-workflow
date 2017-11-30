# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_user_task_sale_line_map_ids = fields.One2many(
        comodel_name='project.user.task.sale_line.map',
        inverse_name='task_id',
        string='Project user task mapping',
    )
    project_uses_task_sale_line_map = fields.Boolean(
        related='project_id.project_uses_task_sale_line_map',
        readonly=True,
        string='Project uses user task mapping',
    )
