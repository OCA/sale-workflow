# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectUserTaskSalelineMap(models.Model):
    _name = 'project.user.task.sale_line.map'

    @api.constrains('project_id', 'user_id', 'task_id',)
    def _check_unique_project_user_task(self):
        domain = [
            ('project_id', '=', self.project_id.id or False),
            ('user_id', '=', self.user_id.id or False),
            ('task_id', '=', self.task_id.id or False),
            ('id', '!=', self.id),
        ]
        if self.search(domain):
            raise ValidationError(_(
                'A project user task mapping must be unique '
                'by project, user and task!'
            ))

    name = fields.Char(
        compute='_compute_name',
        readonly=True,
        store=True,
    )

    @api.depends('user_id', 'task_id')
    def _compute_name(self):
        for mapping in self:
            mapping.name = mapping.user_id.name or ''
            if mapping.task_id:
                mapping.name += ': ' + mapping.task_id.name

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        required=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=True,
    )
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
    )
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale order line',
        required=True,
    )
