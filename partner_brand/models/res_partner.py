# -*- coding: utf-8 -*-
# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'
    
    type = fields.Selection(selection_add=[('brand', 'Brand')])
