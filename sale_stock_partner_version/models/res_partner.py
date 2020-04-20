# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _version_impacted_tables(self):
        res = super(ResPartner, self)._version_impacted_tables()
        tables = ['procurement_order', 'stock_picking', 'stock_move']
        res.extend(tables)
        return res
