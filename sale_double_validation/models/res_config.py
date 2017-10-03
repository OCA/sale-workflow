# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class SaleConfig(models.TransientModel):

    _inherit = 'sale.config.settings'

    so_double_validation = fields.Selection([
        ('one_step', 'Confirm sale orders in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a sale order')
        ], related="company_id.so_double_validation",
        string="Levels of Approvals *",
        help="Provide a double validation mechanism for purchases")

    so_double_validation_amount = fields.Monetary(
        related="company_id.so_double_validation_amount",
        string="Double validation amount *", default=5000,
        help="Minimum amount for which a double validation is required",
        currency_field="company_currency_id")

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
        help="Utility field to express amount currency")
