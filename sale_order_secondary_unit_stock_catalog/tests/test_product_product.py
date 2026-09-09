# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestProductProduct(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        tmpl_sec = cls.env["product.template"].create(
            {
                "name": "Test Product Secondary",
                "is_storable": True,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "slice",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        }
                    )
                ],
            }
        )
        cls.product_sec = tmpl_sec.product_variant_id
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", tmpl_sec.id)]
        )
        cls.product_sec.sale_secondary_uom_id = cls.secondary_unit

        tmpl_no_sec = cls.env["product.template"].create(
            {
                "name": "Test Product No Secondary",
                "is_storable": True,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
            }
        )
        cls.product_no_sec = tmpl_no_sec.product_variant_id

        cls.env["stock.quant"].sudo()._update_available_quantity(
            cls.product_sec, cls.stock_location, 10.0
        )
        cls.env["stock.quant"].sudo()._update_available_quantity(
            cls.product_no_sec, cls.stock_location, 10.0
        )

        tmpl_indep = cls.env["product.template"].create(
            {
                "name": "Test Product Independent",
                "is_storable": True,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "slice-indep",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                            "dependency_type": "independent",
                        }
                    )
                ],
            }
        )
        cls.product_indep = tmpl_indep.product_variant_id
        cls.secondary_unit_indep = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", tmpl_indep.id)]
        )
        cls.product_indep.sale_secondary_uom_id = cls.secondary_unit_indep
        cls.env["stock.quant"].sudo()._update_available_quantity(
            cls.product_indep, cls.stock_location, 10.0
        )

        tmpl_zero = cls.env["product.template"].create(
            {
                "name": "Test Product Zero Stock",
                "is_storable": True,
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "slice-zero",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        }
                    )
                ],
            }
        )
        cls.product_zero = tmpl_zero.product_variant_id
        secondary_unit_zero = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", tmpl_zero.id)]
        )
        cls.product_zero.sale_secondary_uom_id = secondary_unit_zero

    def test_no_catalog_context_returns_zero(self):
        self.assertEqual(self.product_sec.sale_secondary_unit_qty_available, 0.0)
        self.assertFalse(self.product_sec.has_sale_secondary_unit_qty_available)

    def test_catalog_context_with_dependent_secondary_unit(self):
        product = self.product_sec.with_context(
            product_catalog_order_model="sale.order"
        )
        # 10 kg / factor 0.5 = 20 slices
        self.assertEqual(product.sale_secondary_unit_qty_available, 20.0)
        self.assertTrue(product.has_sale_secondary_unit_qty_available)

    def test_catalog_context_no_secondary_unit(self):
        product = self.product_no_sec.with_context(
            product_catalog_order_model="sale.order"
        )
        self.assertEqual(product.sale_secondary_unit_qty_available, 0.0)
        self.assertFalse(product.has_sale_secondary_unit_qty_available)

    def test_catalog_context_independent_secondary_unit(self):
        product = self.product_indep.with_context(
            product_catalog_order_model="sale.order"
        )
        self.assertEqual(product.sale_secondary_unit_qty_available, 0.0)
        self.assertFalse(product.has_sale_secondary_unit_qty_available)

    def test_catalog_context_zero_stock(self):
        product = self.product_zero.with_context(
            product_catalog_order_model="sale.order"
        )
        self.assertEqual(product.sale_secondary_unit_qty_available, 0.0)
        self.assertFalse(product.has_sale_secondary_unit_qty_available)
