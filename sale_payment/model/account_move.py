# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sale_ids = fields.Many2many(comodel_name='sale.order',
                                string='Sales Orders')
