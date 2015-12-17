# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
# from openerp.exceptions import Warning


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _get_project(self, procurement):
        # Search project assigned by another line
        project_obj = self.env['project.project']
        order = procurement.sale_line_id.order_id
        # if not order.project_id and len(order.mapped('order_line.product_id.project_id')) > 1:
        #     raise Warning(_("""Order policy is not analytic and different projects in lines. You must assign project in sale order"""))
        project = order.task_ids and order.task_ids[0].project_id or False
        order_project_id = order.project_id and project_obj.search(
            [('analytic_account_id', '=', order.project_id.id)]) or False
        if order.order_policy == 'analytic':
            parent = procurement.product_id.project_id or order_project_id
        else:
            parent = order_project_id

        if not project:
            vals = self._prepare_project(procurement, parent)
            project = project_obj.create(vals)
            order.project_id = project.analytic_account_id.id
        elif (order.order_policy == 'analytic' and project != parent):
            vals = self._prepare_project(procurement, parent)
            project = project_obj.create(vals)
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
                'hours': work.hours,
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
            fields.Date.context_today(self))
        res = {
            'user_id': sale_order.user_id.id,
            'name': name,
            'partner_id': sale_order.partner_id.id,
            'pricelist_id': sale_order.pricelist_id.id,
        }
        if parent:
            res['parent_id'] = parent.analytic_account_id.id
        if procurement.sale_line_id.order_id.order_policy == 'analytic':
            res['to_invoice'] = self.env.ref(
                'hr_timesheet_invoice.timesheet_invoice_factor1').id
        return res
