# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SaleReport(models.Model):
    _inherit = 'sale.report'

    commercial_partner_id = fields.Many2one(
        'res.partner', string='Commercial Customer', readonly=True)

    def _select(self):
        sql_str = super(SaleReport, self)._select()
        sql_str += ', s.commercial_partner_id as commercial_partner_id'
        return sql_str

    def _group_by(self):
        sql_str = super(SaleReport, self)._group_by()
        sql_str += ', s.commercial_partner_id'
        return sql_str
