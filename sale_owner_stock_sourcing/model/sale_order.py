# -*- coding: utf-8 -*-
# © 2015-2015 Yannick Vaucher, Leonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    stock_owner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Stock Owner')
