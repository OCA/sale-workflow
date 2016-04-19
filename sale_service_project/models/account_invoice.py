# -*- coding: utf-8 -*-
# © 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# © 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    print_works = fields.Boolean(
        string='Print materials and works', default=True)


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
