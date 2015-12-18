# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _get_project(self, procurement):
        def new_project(parent):
            res = projects.filtered(
                lambda x: x.parent_id == parent)
            if not res:
                vals = self._prepare_project(procurement, parent)
                return self.env['project.project'].create(vals)
            return res
        order = procurement.sale_line_id.order_id
        projects = order.task_ids.mapped('project_id')
        if (order.order_policy == 'analytic' and
                procurement.product_id.project_id):
            project = new_project(
                procurement.product_id.project_id.analytic_account_id)
        else:
            if order.project_id and order.name in order.project_id.name:
                project = self.env['project.project'].search(
                    [('analytic_account_id', '=', order.project_id.id)])
            else:
                project = new_project(order.project_id)
                order.project_id = project.analytic_account_id.id
        return project

    @api.model
    def _create_service_task(self, procurement):
        task_id = super(ProcurementOrder, self)._create_service_task(
            procurement)
        vals = self._prepare_task(procurement)
        self.env['project.task'].browse(task_id).write(vals)
        if procurement.sale_line_id.order_id.order_policy == 'analytic':
            procurement.sale_line_id.order_id.state = 'progress'
        return task_id

    @api.model
    def _prepare_task(self, procurement):
        sale_works = procurement.mapped('sale_line_id.task_work_ids')
        sale_materials = procurement.mapped('sale_line_id.task_materials_ids')
        work_list = []
        material_list = []
        total_work_hours = 0.0
        for work in sale_works:
            work_list.append((0, 0, {
                'name': work.name,
                'hours': False,
                'user_id': self.env.user.id,
            }))
            total_work_hours += work.hours
        for material in sale_materials:
            material_list.append((0, 0, {
                'product_id': material.material_id.id,
                'quantity': material.quantity
            }))
        vals = {'planned_hours': total_work_hours,
                'work_ids': work_list,
                'material_ids': material_list,
                'user_id': procurement.product_id.product_manager.id or
                procurement.sale_line_id.order_id.user_id.id}
        return vals

    @api.model
    def _prepare_project(self, procurement, parent=None):
        sale_order = procurement.sale_line_id.order_id
        name = u" %s - %s" % (
            sale_order.name,
            parent and parent.name or '')
        res = {
            'user_id': sale_order.user_id.id,
            'name': name,
            'partner_id': sale_order.partner_id.id,
            'pricelist_id': sale_order.pricelist_id.id,
        }
        if parent:
            res['parent_id'] = parent.id
        if procurement.sale_line_id.order_id.order_policy == 'analytic':
            res['to_invoice'] = self.env.ref(
                'hr_timesheet_invoice.timesheet_invoice_factor1').id
        return res
