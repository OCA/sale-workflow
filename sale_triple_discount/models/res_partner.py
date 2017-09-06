# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_discount1 = fields.Float('Default Discount 1 (%)')
    default_discount2 = fields.Float('Default Discount 2 (%)')
    default_discount3 = fields.Float('Default Discount 3 (%)')
