# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SavepointCase


class SaleOrderServiceLevelTest(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product1 = cls.env["product.product"].create(
            {"name": "test_product1", "type": "product"}
        )
        cls.service_level_sdt = cls.env["stock.service.level"].create(
            {
                "name": "Standard",
                "code": "STD",
            }
        )
        cls.order = cls.env["sale.order"].create(
            [
                {
                    "partner_id": cls.partner.id,
                    "commitment_date": "2024-02-02",
                    "service_level_id": cls.service_level_sdt.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": cls.product1.name,
                                "product_id": cls.product1.id,
                                "product_uom_qty": 1,
                                "product_uom": cls.product1.uom_id.id,
                            },
                        ),
                    ],
                },
            ]
        )

    def test_confirm_sale_order_propagate_service_level(
        self,
    ):
        self.order.action_confirm()
        delivery = self.order.picking_ids
        self.assertEqual(
            delivery.move_lines.service_level_id,
            self.service_level_sdt,
        )

    def test_confirm_sale_order_without_service_level(
        self,
    ):
        self.order.service_level_id = False
        self.order.action_confirm()
        delivery = self.order.picking_ids
        self.assertFalse(
            delivery.move_lines.service_level_id,
        )
