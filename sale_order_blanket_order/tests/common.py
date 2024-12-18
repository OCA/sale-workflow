# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo import Command, fields, models

from odoo.addons.base.tests.common import BaseCommon


class SaleOrderBlanketOrderCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        """Setup the test

        - Create a partner
        - Create three products (and set their quantity in stock)
        - Create a blanket sale order with 3 lines.
            - 2 lines for product 1
            - 1 line for product 2
            - reservation strategy at_confirm
        - Create a blanket sale order with 3 lines.
            - 2 lines for product 1
            - 1 line for product 2
            - reservation strategy at_call_off
        - Create a normal sale order with 2 lines.
        """
        super().setUpClass()
        # create a flat tax
        cls.tax_fixed = cls.env["account.tax"].create(
            {
                "sequence": 10,
                "name": "Tax 10.0 (Fixed)",
                "amount": 10.0,
                "amount_type": "fixed",
                "include_base_amount": True,
            }
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "taxes_id": [Command.link(cls.tax_fixed.id)],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "product",
                "taxes_id": [Command.link(cls.tax_fixed.id)],
            }
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "type": "product",
                "taxes_id": [Command.link(cls.tax_fixed.id)],
            }
        )
        cls._set_qty_in_loc_only(cls.product_1, 1000)
        cls._set_qty_in_loc_only(cls.product_2, 2000)
        cls.blanket_so = cls.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": cls.partner.id,
                "blanket_validity_start_date": "2025-01-01",
                "blanket_validity_end_date": "2025-12-31",
                "blanket_reservation_strategy": "at_call_off",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 100.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 100.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 200.0,
                        }
                    ),
                ],
            }
        )

        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 100.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 200.0,
                        }
                    ),
                ],
            }
        )
        cls.so_model = cls.env["sale.order"]
        cls.call_off_domain = [("order_type", "=", "call_off")]

        # create a fake model to declare another reservation strategy
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        cls.addClassCleanup(cls.loader.restore_registry)

        # pylint: disable=consider-merging-classes-inherited
        class SO(models.Model):
            _inherit = "sale.order"

            blanket_reservation_strategy = fields.Selection(
                selection_add=[("fake", "For tests")],
                ondelete={"fake": "cascade"},
            )

            def _blanket_order_reserve_call_off_remaining_qty(self):
                # we need to override since our strategy is fake
                (
                    _to_reserve,
                    other_orders,
                ) = self._split_recrodset_for_reservation_strategy("fake")
                return super(
                    SO, other_orders
                )._blanket_order_reserve_call_off_remaining_qty()

            def _blanket_order_release_call_off_remaining_qty(self):
                # we need to override since our strategy is fake
                (
                    _to_release,
                    other_orders,
                ) = self._split_recrodset_for_reservation_strategy("fake")
                return super(
                    SO, other_orders
                )._blanket_order_release_call_off_remaining_qty()

        cls.loader.update_registry([SO])

    @classmethod
    def _set_qty_in_loc_only(cls, product, qty, location=None):
        location = location or cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        ).action_apply_inventory()
