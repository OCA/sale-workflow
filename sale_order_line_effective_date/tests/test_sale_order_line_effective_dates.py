# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from freezegun import freeze_time

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderLineEffectiveDates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("stock.picking_type_out").create_backorder = "always"
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 10,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.product.uom_id.id,
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
        first_picking.move_ids.write({"quantity_done": 3.0})
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
        second_picking.move_ids.write({"quantity_done": 7.0})
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
