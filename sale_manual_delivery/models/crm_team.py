# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    manual_delivery = fields.Boolean(
        string='Manual Delivery',
        default=False
    )
