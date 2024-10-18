# Copyright 2022-2023 Michael Tietz (MT Software) <mtietz@mt-software.de>

from odoo.tests import Form

from odoo.addons.sale.tests.common import TestSaleCommonBase
from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import (
    ValuationReconciliationTestCommon,
)


class TestServiceQtyDeliveredCommon(
    TestSaleCommonBase, ValuationReconciliationTestCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Stockable", "type": "product", "invoice_policy": "delivery"}
        )
        cls.delivery = cls.product.create(
            {"name": "Service", "type": "service", "invoice_policy": "delivery"}
        )

    def _new_sale_order(self):
        warehouse = self.company_data["default_warehouse"]
        self.env["stock.quant"]._update_available_quantity(
            self.product, warehouse.lot_stock_id, 10
        )
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.main_partner").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.delivery.id,
                            "product_uom_qty": 1,
                            "product_uom": self.delivery.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                ],
                "picking_policy": "direct",
            }
        )

    def _check_qty_delivered(self, sum_qty_delivered):
        self.so.flush()
        self.so.order_line.flush()
        self.assertEqual(
            sum(self.so.order_line.mapped("qty_delivered")), sum_qty_delivered
        )

    def _deliver_order(self):
        pick = self.so.picking_ids
        pick.move_lines.write({"quantity_done": 1})
        pick.button_validate()

    def _return_order(self):
        # Create return picking
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.so.picking_ids.ids,
                active_id=self.so.picking_ids.id,
                active_model="stock.picking",
            )
        )
        return_wiz = stock_return_picking_form.save()
        return_wiz.product_return_moves.quantity = 1.0
        return_wiz.product_return_moves.to_refund = True
        res = return_wiz.create_returns()
        return_pick = self.env["stock.picking"].browse(res["res_id"])

        # Validate picking
        return_pick.move_lines.write({"quantity_done": 1})
        return_pick.button_validate()
