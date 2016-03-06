# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Sergio Teruel
# © 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    print_works = fields.Boolean(
        string='Print materials and works', default=True)
    task_ids = fields.One2many(
        comodel_name='project.task',
        compute='_compute_tasks',
        string='Tasks')
    invoice_on_timesheets = fields.Boolean(
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    task_closed = fields.Boolean(compute='_compute_tasks')
    has_task = fields.Boolean(compute='_compute_tasks')

    @api.multi
    def _compute_tasks(self):
        for order in self:
            tasks = order.mapped('order_line.task_ids')
            order.task_ids = tasks
            order.has_task = bool(tasks)
            order.task_closed = all(order.mapped('order_line.task_closed'))

    @api.model
    def test_no_product(self, order):
        if order.invoice_on_timesheets:
            return False
        else:
            return super(SaleOrder, self).test_no_product(order)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        project = self.env['project.project'].search(
            [('analytic_account_id', '=', self.project_id.id)])
        self.invoice_on_timesheets = project.invoice_on_timesheets

    @api.multi
    def action_view_task(self):
        task_ids = self.mapped('task_ids')
        result = self.env.ref('project.action_view_task').read()[0]
        if len(task_ids) != 1:
            result['domain'] = "[('id', 'in', %s)]" % task_ids.ids
        else:
            res = self.env.ref('project.view_task_form2', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = task_ids.id
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    auto_create_task = fields.Boolean(
        related='product_id.auto_create_task', readonly=True)
    task_work_ids = fields.One2many(
        comodel_name='sale.order.line.task.work',
        inverse_name='order_line_id',
        copy=True,
        string='Works')
    task_materials_ids = fields.One2many(
        comodel_name='sale.order.line.task.materials',
        inverse_name='order_line_id',
        copy=True,
        string='Materials')
    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='sale_line_id',
        string='Tasks')
    task_closed = fields.Boolean(
        compute='_compute_task_closed',
        store=True,
    )

    @api.multi
    @api.depends('task_ids.stage_id.closed')
    def _compute_task_closed(self):
        for line in self:
            line.task_closed = all(line.mapped('task_ids.stage_id.closed'))

    @api.multi
    def product_id_change(
        self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
            name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag)

        product_id = self.product_id.browse(product)
        if product_id.auto_create_task:
            work_list = []
            for work in product_id.task_work_ids:
                work_list.append((0, 0, {
                    'name': work.name,
                    'hours': work.hours
                }))
            material_list = []
            for material in product_id.task_materials_ids:
                material_list.append((0, 0, {
                    'product_id': material.material_id.id,
                    'quantity': material.quantity
                }))
            vals = {'task_work_ids': work_list,
                    'task_materials_ids': material_list}
        else:
            vals = {'task_work_ids': False,
                    'task_materials_ids': False}
        res['value'].update(vals)
        return res


class SaleOrderLineTaskWork(models.Model):
    _name = 'sale.order.line.task.work'

    order_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Order Line')
    name = fields.Char(string='Name')
    hours = fields.Float(
        string='Hours',
        digits_compute=dp.get_precision('Product Unit of Measure'))


class SaleOrderLineTaskMaterials(models.Model):
    _name = 'sale.order.line.task.materials'

    order_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Order Line')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Material')
    quantity = fields.Float(
        string='Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'))
