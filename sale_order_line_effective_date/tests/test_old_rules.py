# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from freezegun import freeze_time

from odoo import fields

from odoo.addons.stock.tests.common import TestStockCommon


class TestSaleOrderLineEffectiveDates(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse_2_steps = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2 steps",
                "code": "2S",
                "reception_steps": "two_steps",
                "delivery_steps": "pick_ship",
            }
        )
        delivery_route_2 = cls.warehouse_2_steps.delivery_route_id
        delivery_route_2.rule_ids[0].write(
            {
                "location_dest_id": delivery_route_2.rule_ids[1].location_src_id.id,
                "name": "2S: Stock → Output",
            }
        )
        delivery_route_2.rule_ids[1].write({"action": "pull"})
        cls.env["stock.picking.type"].browse(
            cls.picking_type_out
        ).create_backorder = "always"
        cls.env["stock.quant"].create(
            {
                "product_id": cls.productA.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 10,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.productA.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.productA.uom_id.id,
                        },
                    )
                ],
            }
        )

    def test_sale_order_line_effective_date(self):
        """Check effective dates are computed correctly."""
        self.sale.action_confirm()
        # No delivery
        self.assertFalse(self.sale.order_line.effective_date)
        self.assertFalse(self.sale.order_line.last_effective_date)
        # First delivery
        first_delivery_dtt = "2024-06-01 00:00:00"
        first_picking = self.sale.picking_ids[0]
        first_picking.action_assign()
        first_picking.move_ids.write({"quantity": 3.0})
        with freeze_time(first_delivery_dtt):
            first_picking.button_validate()
        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "effective_date": fields.Datetime.from_string(first_delivery_dtt),
                    "last_effective_date": fields.Datetime.from_string(
                        first_delivery_dtt
                    ),
                }
            ],
        )
        # Second delivery
        second_delivery_dtt = "2024-07-01 00:00:00"
        second_picking = self.sale.picking_ids[-1]
        second_picking.action_assign()
        second_picking.move_ids.write({"quantity": 7.0})
        with freeze_time(second_delivery_dtt):
            second_picking.button_validate()
        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "effective_date": fields.Datetime.from_string(first_delivery_dtt),
                    "last_effective_date": fields.Datetime.from_string(
                        second_delivery_dtt
                    ),
                }
            ],
        )
