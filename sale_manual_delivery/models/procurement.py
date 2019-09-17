# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    manual_delivery = fields.Boolean(
        string='Manual Delivery',
        default=False,
        help="If Manual, the deliveries are not created at SO confirmation.\
        You need to use the Create Delivery button in order to reserve and \
        ship the goods."
    )
