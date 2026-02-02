# Copyright 2023 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.sale_order_line_cancel.tests.common import (
    TestSaleOrderLineCancelBase as Base,
)


class TestSaleOrderLineCancelBase(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.warehouse.lot_stock_id, 10.0
        )

    @classmethod
    def _prepare_product_vals(cls):
        vals = super()._prepare_product_vals()
        vals["type"] = "product"
        return vals

    @classmethod
    def _add_done_sale_order(cls, **kwargs):
        if "picking_policy" not in kwargs:
            kwargs["picking_policy"] = "direct"
        return super()._add_done_sale_order(**kwargs)
