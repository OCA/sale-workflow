# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleStockOrderSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
            }
        )
        # Set secondary uom on product template
        cls.product.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "unit-700",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.7,
                        },
                    )
                ],
            }
        )
        StockQuant = cls.env["stock.quant"]
        StockQuant.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 2000,
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product.product_tmpl_id.id)]
        )
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
        # A second product, kept out of the order, to be added from the catalog
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "test 2",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "list_price": 100.00,
            }
        )
        cls.product_2.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "unit-700-2",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.7,
                        },
                    )
                ],
            }
        )
        cls.secondary_unit_2 = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product_2.product_tmpl_id.id)]
        )
        cls.product_2.sale_secondary_uom_id = cls.secondary_unit_2.id
        StockQuant.create(
            {
                "product_id": cls.product_2.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 2000,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        so = cls.env["sale.order"].new(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
            }
        )
        so._onchange_partner_id_warning()
        cls.order = cls.env["sale.order"].create(so._convert_to_write(so._cache))

    def test_stock_move_line_secondary_unit(self):
        self.order.order_line.write(
            {"secondary_uom_id": self.secondary_unit.id, "secondary_uom_qty": 5}
        )
        self.order.order_line._onchange_helper_product_uom_for_secondary()
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertEqual(picking.move_line_ids.secondary_uom_qty, 5.0)

    def _catalog_line(self, product):
        return self.order.order_line.filtered(lambda line: line.product_id == product)

    def test_catalog_new_line_on_confirmed_order(self):
        """Adding a product from the catalog to a confirmed order must move the
        secondary unit to the generated move, not the secondary quantity into
        the product quantity.
        """
        self.order.action_confirm()
        self.order._update_order_line_info(self.product_2.id, 5)
        line = self._catalog_line(self.product_2)
        self.assertEqual(line.secondary_uom_id, self.secondary_unit_2)
        self.assertEqual(line.secondary_uom_qty, 5.0)
        self.assertEqual(line.product_uom_qty, 3.5)
        self.assertEqual(line.move_ids.secondary_uom_id, self.secondary_unit_2)
        self.assertEqual(line.move_ids.secondary_uom_qty, 5.0)
        self.assertEqual(line.move_ids.product_uom_qty, 3.5)

    def test_catalog_update_line_on_confirmed_order(self):
        """Raising the catalog quantity of an existing line must propagate the
        delta to the moves in both units.
        """
        self.order.action_confirm()
        self.order._update_order_line_info(self.product_2.id, 5)
        self.order._update_order_line_info(self.product_2.id, 8)
        line = self._catalog_line(self.product_2)
        self.assertEqual(line.secondary_uom_qty, 8.0)
        self.assertEqual(line.product_uom_qty, 5.6)
        moves = line.move_ids.filtered(lambda move: move.state != "cancel")
        self.assertEqual(sum(moves.mapped("product_uom_qty")), 5.6)
        self.assertEqual(sum(moves.mapped("secondary_uom_qty")), 8.0)
