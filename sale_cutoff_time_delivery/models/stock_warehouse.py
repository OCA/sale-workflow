# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models

from odoo.addons.base.models.res_partner import _tz_get


class StockWarehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["stock.warehouse", "time.cutoff.mixin"]

    apply_cutoff = fields.Boolean()
    tz = fields.Selection(_tz_get, string="Timezone")

    def get_cutoff_time(self):
        res = super().get_cutoff_time()
        res["tz"] = self.tz
        return res
