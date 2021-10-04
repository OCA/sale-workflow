# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form
from odoo.tests.common import SavepointCase

from odoo.addons.sale_purchase_amendment.tests.common import CommonPurchaseAmendment


class TestSalePurchaseAmendment(CommonPurchaseAmendment):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env["sale.order.line.route.amend"]

    def _create_amend_wizard(self, values=None):
        if values is None:
            values = {}
        if "route_id" not in values:
            values.update(
                {
                    "route_id": self.route_drop.id,
                }
            )
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_id=self.sale_order.id
        ).create(values)
        return True

    def test_amend_route_mto(self):
        """
        Create and confirm a sale order with MTO route
        The created move will use the default route Stock > Customers
        and purchase order

        Launch the wizard to update the route and select the drop shipping
        route.

        A new move is created from Vendors > Customers
        """
        self.warehouse.mto_pull_id.active = True
        self.warehouse.mto_pull_id.route_id.active = True
        # Force a Purchase Order
        self.warehouse.mto_pull_id.procure_method = "make_to_order"
        # Add Buy to product
        self.product.route_ids |= self.warehouse.buy_pull_id.route_id
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "route_id": self.warehouse.mto_pull_id.route_id.id,
                        },
                    )
                ],
            }
        )
        self.sale_order.action_confirm()

        purchase_line = self.sale_order.order_line.chained_purchase_line_ids

        self.assertTrue(purchase_line)
        self.assertEqual(self.product, purchase_line.product_id)

        self._create_amend_wizard({"route_id": False})
        wizard_form = Form(self.wizard)
        wizard_form.route_id = self.env["stock.location.route"].browse()
        wizard = wizard_form.save()
        wizard.update_route()

        purchase_line = self.sale_order.order_line.chained_purchase_line_ids

        self.assertEqual(0, len(purchase_line))

        self._create_amend_wizard({"route_id": self.warehouse.mto_pull_id.route_id.id})
        wizard_form = Form(self.wizard)
        wizard_form.route_id = self.warehouse.mto_pull_id.route_id
        wizard = wizard_form.save()
        wizard.update_route()

        purchase_line = self.sale_order.order_line.chained_purchase_line_ids

        self.assertEqual(1, len(purchase_line))


class SalePurchaseRouteAmendmentTest(TestSalePurchaseAmendment, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
