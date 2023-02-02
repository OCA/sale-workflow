# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleOrderLineCancelBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "type": "product",
                "sale_ok": True,
                "active": True,
            }
        )
        cls.product_2 = cls.product_1.copy({"name": "test product 2"})
        cls.product_3 = cls.product_1.copy({"name": "test product 3"})
        cls.sale = cls._add_done_sale_order()
        cls.sale.action_done()
        cls.wiz = cls.env["sale.order.line.cancel"].create({})
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.warehouse.lot_stock_id, 10.0
        )

    @classmethod
    def _add_done_sale_order(
        cls, partner=None, product=None, qty=10, picking_policy="direct"
    ):
        if partner is None:
            partner = cls.partner
        if product is None:
            product = cls.product_1
        warehouse = cls.warehouse
        sale_order_model = cls.env["sale.order"]
        lines = [
            Command.create(
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": qty,
                    "product_uom": p.uom_id.id,
                    "price_unit": 1,
                },
            )
            for p in product
        ]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": lines,
        }
        if picking_policy:
            so_values["picking_policy"] = picking_policy
        so = sale_order_model.create(so_values)
        so.action_confirm()
        so.action_done()
        return so
