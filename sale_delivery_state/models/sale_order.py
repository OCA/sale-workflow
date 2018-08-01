# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_state = fields.Selection([
        ('unprocessed', 'Unprocessed'),
        ('partially', 'Partially processed'),
        ('done', 'Done')],
        string='Picking state',
        copy=False,
        default='unprocessed'
    )
