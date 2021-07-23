# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    _sql_constraints = [
        ("name_ref_uniq", "unique (name)", "Serial Numbers must be Globally Unique!"),
    ]
