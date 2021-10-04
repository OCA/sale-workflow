# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase

from .common import CommonPurchaseAmendment


class TestSalePurchaseAmendment(CommonPurchaseAmendment):
    def test_sale_purchase_decrease(self):
        """
        Create and confirm a sale order with MTO route and product qty == 2.0
        The created move will use the default route Stock > Customers
        and purchase order

        Decrease quantity to 1.0 in SO
        Purchase line quantity should be set to 1.0

        Increase quantity to 3.0 in SO
        Purchase line quantity should be set to 3.0
        """
        self.warehouse.mto_pull_id.active = True
        self.warehouse.mto_pull_id.route_id.active = True
        self.warehouse.mto_pull_id.procure_method = "make_to_order"
        self.product.route_ids |= self.warehouse.buy_pull_id.route_id

        self._create_sale_order()

        self.sale_order.action_confirm()

        purchase_line = self.sale_order.order_line.chained_purchase_line_ids

        self.assertTrue(purchase_line)
        self.assertEqual(self.product, purchase_line.product_id)

        self.assertEqual(2.0, purchase_line.product_uom_qty)

        self.sale_order.order_line.product_uom_qty = 1.0

        purchase_line = self.sale_order.order_line.chained_purchase_line_ids

        self.assertEqual(1, len(purchase_line))
        self.assertEqual(1.0, purchase_line.product_uom_qty)

        self.sale_order.order_line.product_uom_qty = 3.0
        purchase_line = self.sale_order.order_line.chained_purchase_line_ids
        self.assertEqual(1, len(purchase_line))
        self.assertEqual(3.0, purchase_line.product_uom_qty)

        purchase_line.order_id.button_confirm()

        self.assertFalse(self.sale_order.order_line.can_amend_and_reprocure)

        self.sale_order.order_line.product_uom_qty = 2.0


class SalePurchaseAmendmentTest(TestSalePurchaseAmendment, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
