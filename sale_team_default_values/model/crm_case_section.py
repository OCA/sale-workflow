# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Author: Guewen Baconnier, Leonardo Pistone
# Copyright 2014-2015 Camptocamp SA

from openerp import models, fields


class CrmCaseSection(models.Model):
    _inherit = 'crm.case.section'

    pricelist_id = fields.Many2one(comodel_name='product.pricelist',
                                   string='Pricelist')
    payment_term = fields.Many2one(comodel_name='account.payment.term',
                                   string='Payment Term',
                                   oldname='payment_term_id')
    fiscal_position = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal Position',
        oldname='fiscal_position_id',
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
    )
    project = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        domain=[('type', '!=', 'view'),
                ('state', 'not in', ('close', 'cancelled'))],
        oldname='account_analytic_id',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
    )
