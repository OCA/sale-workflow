# -*- coding: utf-8 -*-
# © 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# © 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    task_work_ids = fields.One2many(
        comodel_name='product.task.work', inverse_name='product_id',
        string='Task Works')
    task_materials_ids = fields.One2many(
        comodel_name='product.task.materials', inverse_name='product_id',
        string='Materials')

    @api.multi
    def action_compute_price(self):
        wiz = {
            'name': _("Compute Service Price"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'product.price.service.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': {}
            }
        return wiz


class ProductTaskWork(models.Model):
    _name = 'product.task.work'
    _order = 'sequence'

    product_id = fields.Many2one(
        comodel_name='product.template', string='Product', ondelete='restrict')
    name = fields.Char(string='Name')
    hours = fields.Float(
        string='Hours',
        digits=dp.get_precision('Product Unit of Measure'))
    sequence = fields.Integer()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def action_compute_price(self):
        ctx = dict(self.env.context.copy(), active_id=self.product_tmpl_id.id)
        wiz = {
            'name': _("Compute Service Price"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'product.price.service.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx
            }
        return wiz


class ProductTaskMaterials(models.Model):
    _name = 'product.task.materials'
    _order = 'sequence'

    product_id = fields.Many2one(
        comodel_name='product.template', string='Product', ondelete='restrict')
    material_id = fields.Many2one(
        comodel_name='product.product', string='Material', required=True)
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    sequence = fields.Integer()
