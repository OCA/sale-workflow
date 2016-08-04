# -*- coding: utf-8 -*-
# © 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# © 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from openerp.tools.translate import _


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
    sale_line_id = fields.Many2one(index=True)
    analytic_line_ids = fields.One2many(comodel_name='account.analytic.line',
                                        compute='_compute_analytic_line_ids')
    invoice_ids = fields.One2many(comodel_name='account.invoice',
                                  compute='_compute_analytic_line_ids')
    all_invoiced = fields.Boolean(compute='_compute_analytic_line_ids')
    invoice_exists = fields.Boolean(compute='_compute_analytic_line_ids')
    is_closed = fields.Boolean(compute='_compute_analytic_line_ids')

    @api.multi
    def _compute_analytic_line_ids(self):
        for task in self:
            all_inv = True
            invoice_ids = []
            lines = task.mapped('work_ids.hr_analytic_timesheet_id.line_id')
            if 'analytic_line_id' in task.material_ids._all_columns:
                lines = lines | task.mapped('material_ids.analytic_line_id')
            for line in lines:
                if line.invoice_id:
                    invoice_ids.append(line.invoice_id.id)
                elif line.to_invoice:
                    all_inv = False
            task.analytic_line_ids = lines
            task.invoice_ids = invoice_ids
            task.invoice_exists = bool(invoice_ids)
            task.all_invoiced = all_inv
            task.is_closed = task.stage_id.closed

    @api.multi
    def action_create_invoice(self):
        lines = self.analytic_line_ids.filtered(
            lambda x: x.to_invoice and not x.invoice_id)
        return {
            'name': _('Create Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.timesheet.invoice.create',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': dict(self.env.context or {}, active_ids=lines.ids),
        }

    @api.multi
    def action_view_invoice(self):
        result = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(self.invoice_ids) != 1:
            result['domain'] = "[('id', 'in', %s)]" % self.invoice_ids.ids
        else:
            res = self.env.ref('account.invoice_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result
