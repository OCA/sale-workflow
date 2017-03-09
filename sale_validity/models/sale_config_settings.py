# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    default_sale_order_validity_days = fields.Integer(
        related='company_id.default_sale_order_validity_days')
