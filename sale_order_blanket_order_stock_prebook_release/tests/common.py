# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import Command, fields

from odoo.addons.stock_available_to_promise_release.tests import common


class SaleOrderBlanketOrderStockPrebookReleaseCase(common.PromiseReleaseCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh.delivery_route_id.write({"available_to_promise_defer_pull": True})

        cls.blanket_so = cls.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": cls.partner_delta.id,
                "blanket_validity_start_date": "2025-01-01",
                "blanket_validity_end_date": "2025-12-31",
                "blanket_reservation_strategy": "at_confirm",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product1.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 100.0,
                        }
                    ),
                ],
            }
        )

    def _date_to_datetime(self, date, nb_seconds=0):
        dt = fields.Datetime.to_datetime(date)
        if dt and nb_seconds:
            dt += timedelta(seconds=nb_seconds)
        return dt
