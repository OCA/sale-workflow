# -*- coding: utf-8 -*-
# © 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# © 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _get_project(self, procurement):
        order = procurement.sale_line_id.order_id
        parent = order.project_id
        if parent and order.name in parent.name:
            project = self.env['project.project'].search(
                [('analytic_account_id', '=', parent.id)])
        else:
            vals = self._prepare_project(procurement)
            if parent:
                vals.update({
                    'parent_id': parent.id,
                    'to_invoice': parent.to_invoice.id,
                })
            if not parent.to_invoice and order.invoice_on_timesheets:
                vals['to_invoice'] = self.env.ref(
                    'hr_timesheet_invoice.timesheet_invoice_factor1').id
            project = self.env['project.project'].create(vals)
            order.project_id = project.analytic_account_id.id
        return project

    @api.model
    def _create_service_task(self, procurement):
        task_id = super(ProcurementOrder, self)._create_service_task(
            procurement)
        vals = self._prepare_task(procurement)
        self.env['project.task'].browse(task_id).write(vals)
        if procurement.sale_line_id.order_id.project_id.invoice_on_timesheets:
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
                'product_id': material.product_id.id,
                'quantity': material.quantity
            }))
        vals = {'planned_hours': total_work_hours,
                'work_ids': work_list,
                'material_ids': material_list,
                'user_id': procurement.product_id.product_manager.id or
                procurement.sale_line_id.order_id.user_id.id}
        return vals

    @api.model
    def _prepare_project(self, procurement):
        sale_order = procurement.sale_line_id.order_id
        res = {
            'user_id': sale_order.user_id.id,
            'name': sale_order.name,
            'partner_id': sale_order.partner_id.id,
            'pricelist_id': sale_order.pricelist_id.id,
            'invoice_on_timesheets': sale_order.invoice_on_timesheets,
        }
        return res
