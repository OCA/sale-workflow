# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
from openerp.addons.decimal_precision import decimal_precision as dp
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_policy = fields.Selection(selection_add=[('analytic', 'Analytic')])
    task_ids = fields.One2many(
        comodel_name='project.task',
        compute='_compute_task_ids',
        string='Tasks')

    def _compute_task_ids(self):
        for order in self:
            self.task_ids = self.env['project.task'].search(
                [('sale_line_id', 'in', order.order_line.ids)])

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and not res['fields'].get(
                'order_policy', False):
            xml_form = etree.fromstring(res['arch'])
            placeholder = xml_form.xpath("//field[@name='user_id']")
            placeholder[0].addnext(etree.Element(
                'field', {'name': 'order_policy'}))
            res['arch'] = etree.tostring(xml_form)
            select_values = self._columns['order_policy'].selection
            res['fields'].update(
                {'order_policy': {
                    'string': _('Order Policy'),
                    'type': 'selection',
                    'selection': select_values}})
        return res

    @api.multi
    def action_view_task(self):
        task_ids = self.mapped('task_ids')
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('project.action_view_task')
        list_view_id = imd.xmlid_to_res_id('project.view_task_tree2')
        form_view_id = imd.xmlid_to_res_id('project.view_task_form2')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [
                [list_view_id, 'tree'],
                [form_view_id, 'form'],
                [False, 'graph'],
                [False, 'kanban'],
                [False, 'calendar'],
                [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(task_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % task_ids.ids
        elif len(task_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = task_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    auto_create_task = fields.Boolean(
        related='product_id.auto_create_task', readonly=True)
    task_work_ids = fields.One2many(
        comodel_name='sale.order.line.task.work', inverse_name='order_line_id',
        string='Works')
    task_materials_ids = fields.One2many(
        comodel_name='sale.order.line.task.materials',
        inverse_name='order_line_id', string='Materials')

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
                    'material_id': material.material_id.id,
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
    hours = fields.Float(string='Hours')


class SaleOrderLineTaskMaterials(models.Model):
    _name = 'sale.order.line.task.materials'

    order_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Order Line')
    material_id = fields.Many2one(
        comodel_name='product.product', string='Material')
    quantity = fields.Float(
        string='Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'))
