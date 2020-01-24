# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    end_user_id = fields.Many2one(
        comodel_name='res.partner',
        string='End User',
        index=True,
        domain=[('type', '=', 'end_user')],
        ondelete='restrict',
    )
