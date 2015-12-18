# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    task_hours = fields.Float(compute='_compute_task_hours', store=True)

    @api.multi
    @api.depends('parent_id', 'child_ids', 'tasks',
                 'tasks.work_ids', 'tasks.work_ids.hours')
    def _compute_task_hours(self):
        for project in self:
            project.task_hours = sum(project.tasks.mapped('work_ids.hours'))


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_parent_id = fields.Many2one(
        related='project_id.parent_id',
        store=True,
        string='Project Parent')
