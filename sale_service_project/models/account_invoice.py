# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    print_works = fields.Boolean(
        string='Print materials and works', default=True)
    # task_ids = fields.One2many(
    #     comodel_name='project.task',
    #     compute='_compute_task_ids',
    #     string='Tasks')
    #
    # @api.multi
    # def _compute_task_ids(self):
    #     for inv in self:
    #         tasks = self.env['project.task'].search([
    #             ('work_ids.hr_analytic_timesheet_id.line_id.invoice_id',
    #              '=', inv.id)])
    #         if 'analytic_line_id' in tasks.material_ids._all_columns:
    #             tasks = tasks | self.env['project.task'].search([
    #                 ('material_ids.analytic_line_id.invoice_id.id',
    #                  '=', inv.id)])
    #         self.task_ids = tasks


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    sale_order_lines = fields.Many2many(
        comodel_name='sale.order.line',
        relation='sale_order_line_invoice_rel',
        column1='invoice_id', column2='order_line_id',
        readonly=True, string='Sale Order Lines')
    task_work_ids = fields.Many2many(
        comodel_name='project.task.work',
        column1='invoice_line_id', column2='work_line_id',
        readonly=True, string='Works')
    task_materials_ids = fields.Many2many(
        comodel_name='project.task.materials',
        column1='invoice_line_id', column2='material_line_id',
        readonly=True, string='Materials')
