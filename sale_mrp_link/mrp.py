# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order', 'Source Sale Order')
