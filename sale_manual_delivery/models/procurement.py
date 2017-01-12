# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Delivery Method",
    )
