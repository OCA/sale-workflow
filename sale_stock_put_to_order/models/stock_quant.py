# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _search_pto(self, locations, products):
        """Return quants with positive stock for *products* in *locations*."""
        return self.search(
            [
                ("location_id", "in", locations.ids),
                ("product_id", "in", products.ids),
                ("quantity", ">", 0),
            ]
        )
