# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Sergio Teruel
# © 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models, api
from openerp.report.report_sxw import rml_parse


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


class SaleOrderReport(models.AbstractModel):
    _name = 'report.account.report_invoice'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('account.report_invoice')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'formatLang':rml_parse(
                self.env.cr, self.env.uid, 'account.report_invoice'
            ).formatLang,
        }
        return report_obj.render('account.report_invoice', docargs)
