# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command
from odoo.tests import HttpCase, tagged

from odoo.addons.sale.tests.common import SaleCommon


@tagged("post_install", "-at_install")
class TestSaleOrderCatalog(HttpCase, SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")

        cls.product_sec = cls.env["product.product"].create(
            {
                "name": "Test Product Secondary",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "taxes_id": [Command.clear()],
            }
        )
        cls.product_sec.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "slice",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        }
                    )
                ]
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product_sec.product_tmpl_id.id)]
        )
        cls.product_sec.sale_secondary_uom_id = cls.secondary_unit

        cls.product_indep = cls.env["product.product"].create(
            {
                "name": "Test Product Independent",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "taxes_id": [Command.clear()],
            }
        )
        cls.product_indep.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "name": "slice-indep",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                            "dependency_type": "independent",
                        }
                    )
                ]
            }
        )
        cls.secondary_unit_indep = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product_indep.product_tmpl_id.id)]
        )
        cls.product_indep.sale_secondary_uom_id = cls.secondary_unit_indep

        cls.product_no_sec = cls.env["product.product"].create(
            {
                "name": "Test Product No Secondary",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "taxes_id": [Command.clear()],
            }
        )

    def setUp(self):
        super().setUp()
        self.authenticate(self.sale_manager.login, self.sale_manager.login)
        self.order = self.env["sale.order"].create({"partner_id": self.partner.id})

    def _catalog_update(self, product, quantity):
        response = self.opener.post(
            url=self.base_url() + "/product/catalog/update_order_line_info",
            json={
                "params": {
                    "res_model": "sale.order",
                    "order_id": self.order.id,
                    "product_id": product.id,
                    "quantity": quantity,
                },
            },
        )
        self.order.invalidate_recordset()
        return response.json()["result"]

    def test_catalog_update_creates_line_with_dependent_secondary_unit(self):
        self._catalog_update(self.product_sec, 6)
        sol = self.order.order_line
        self.assertEqual(len(sol), 1)
        self.assertEqual(sol.product_uom_qty, 3.0)  # 6 * 0.5
        self.assertEqual(sol.secondary_uom_qty, 6.0)
        self.assertEqual(sol.secondary_uom_id, self.secondary_unit)

    def test_catalog_update_existing_line_dependent_secondary_unit(self):
        self._catalog_update(self.product_sec, 6)
        self._catalog_update(self.product_sec, 10)
        sol = self.order.order_line
        self.assertEqual(len(sol), 1)
        self.assertEqual(sol.product_uom_qty, 5.0)  # 10 * 0.5
        self.assertEqual(sol.secondary_uom_qty, 10.0)

    def test_catalog_update_no_secondary_unit_standard_behavior(self):
        self._catalog_update(self.product_no_sec, 5)
        sol = self.order.order_line
        self.assertEqual(sol.product_uom_qty, 5.0)
        self.assertFalse(sol.secondary_uom_id)

    def test_catalog_update_independent_no_conversion(self):
        self._catalog_update(self.product_indep, 5)
        sol = self.order.order_line
        self.assertEqual(sol.product_uom_qty, 5.0)

    def test_catalog_lines_data_single_line_shows_secondary_qty(self):
        self.order.order_line = [
            Command.create(
                {
                    "product_id": self.product_sec.id,
                    "product_uom_qty": 3.0,
                    "secondary_uom_id": self.secondary_unit.id,
                }
            )
        ]
        res = self.order.order_line._get_product_catalog_lines_data()
        self.assertEqual(res["quantity"], 6.0)  # 3.0 / 0.5

    def test_catalog_lines_data_multiple_lines_sums_secondary_qty(self):
        self.order.order_line = [
            Command.create(
                {
                    "product_id": self.product_sec.id,
                    "product_uom_qty": 3.0,
                    "secondary_uom_id": self.secondary_unit.id,
                }
            ),
            Command.create(
                {
                    "product_id": self.product_sec.id,
                    "product_uom_qty": 1.5,
                    "secondary_uom_id": self.secondary_unit.id,
                }
            ),
        ]
        res = self.order.order_line._get_product_catalog_lines_data()
        self.assertEqual(res["quantity"], 9.0)  # 6.0 + 3.0

    def test_catalog_lines_data_no_secondary_unit_shows_primary_qty(self):
        self.order.order_line = [
            Command.create(
                {
                    "product_id": self.product_no_sec.id,
                    "product_uom_qty": 5.0,
                }
            )
        ]
        res = self.order.order_line._get_product_catalog_lines_data()
        self.assertEqual(res["quantity"], 5.0)

    def test_catalog_lines_data_independent_shows_primary_qty(self):
        self.order.order_line = [
            Command.create(
                {
                    "product_id": self.product_indep.id,
                    "product_uom_qty": 5.0,
                    "secondary_uom_id": self.secondary_unit_indep.id,
                }
            )
        ]
        res = self.order.order_line._get_product_catalog_lines_data()
        self.assertEqual(res["quantity"], 5.0)
