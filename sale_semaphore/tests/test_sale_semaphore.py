# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleSemaphore(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Semaphore Partner"})
        cls.category = cls.env["product.category"].create(
            {
                "name": "Semaphore Category",
                "semaphore_active": True,
                "semaphore_discount_success": 0.0,
                "semaphore_discount_warning": 10.0,
                "semaphore_discount_danger": 20.0,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Semaphore Product",
                "categ_id": cls.category.id,
                "lst_price": 100.0,
                "standard_price": 50.0,
                "type": "consu",
                "sale_ok": True,
                "semaphore_active": "yes",
                "semaphore_discount_success": 0.0,
                "semaphore_discount_warning": 10.0,
                "semaphore_discount_danger": 20.0,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.salesperson = cls.env["res.users"].create(
            {
                "name": "Semaphore Salesperson",
                "login": "semaphore_salesperson",
                "groups_id": [
                    (6, 0, [cls.env.ref("sales_team.group_sale_salesman").id])
                ],
            }
        )

    def _create_line(self, price_unit):
        return self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "name": self.product.name,
                "product_uom_qty": 1.0,
                "product_uom": self.product.uom_id.id,
                "price_unit": price_unit,
            }
        )

    def test_template_inverse_updates_single_variant(self):
        template = self.product.product_tmpl_id
        template.write(
            {
                "semaphore_active": "yes",
                "semaphore_discount_success": 5.0,
                "semaphore_discount_warning": 12.0,
                "semaphore_discount_danger": 20.0,
            }
        )
        self.assertEqual(self.product.semaphore_active, "yes")
        self.assertEqual(self.product.semaphore_discount_success, 5.0)
        self.assertEqual(self.product.semaphore_discount_warning, 12.0)
        self.assertEqual(self.product.semaphore_discount_danger, 20.0)
        self.assertEqual(template.semaphore_active, "yes")
        self.assertEqual(template.semaphore_discount_success, 5.0)
        self.assertEqual(template.semaphore_discount_warning, 12.0)
        self.assertEqual(template.semaphore_discount_danger, 20.0)

    def test_template_compute_ignores_multiple_variants(self):
        attribute = self.env["product.attribute"].create({"name": "Semaphore Size"})
        value_s = self.env["product.attribute.value"].create(
            {"name": "S", "attribute_id": attribute.id}
        )
        value_m = self.env["product.attribute.value"].create(
            {"name": "M", "attribute_id": attribute.id}
        )
        template = self.env["product.template"].create(
            {
                "name": "Multi Variant Product",
                "type": "consu",
                "list_price": 200.0,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, [value_s.id, value_m.id])],
                        },
                    )
                ],
            }
        )
        self.assertEqual(len(template.product_variant_ids), 2)
        self.assertFalse(template.semaphore_active)
        self.assertEqual(template.semaphore_discount_success, 0.0)
        self.assertEqual(template.semaphore_discount_warning, 0.0)
        self.assertEqual(template.semaphore_discount_danger, 0.0)

    def test_get_semaphore_data_prefers_product_configuration(self):
        data = self.product._get_semaphore_data()
        self.assertEqual(
            data,
            {"success": 0.0, "warning": 10.0, "danger": 20.0},
        )
        self.product.write({"semaphore_active": "no"})
        data = self.product._get_semaphore_data()
        self.assertFalse(data)

    def test_sale_line_computes_semaphore_and_below_limit_flag(self):
        success_line = self._create_line(100.0)
        warning_line = self._create_line(95.0)
        danger_line = self._create_line(85.0)
        below_limit_line = self._create_line(75.0)
        self.assertEqual(success_line.semaphore, "success")
        self.assertEqual(warning_line.semaphore, "warning")
        self.assertEqual(danger_line.semaphore, "danger")
        self.assertEqual(below_limit_line.semaphore, "danger")
        self.assertFalse(success_line.price_below_semaphore)
        self.assertFalse(warning_line.price_below_semaphore)
        self.assertFalse(danger_line.price_below_semaphore)
        self.assertTrue(below_limit_line.price_below_semaphore)
        with self.assertRaises(UserError):
            self.order.with_user(self.salesperson).action_confirm()

    def test_sale_line_uses_category_configuration(self):
        self.product.write(
            {
                "semaphore_active": False,
                "semaphore_discount_success": 0.0,
                "semaphore_discount_warning": 0.0,
                "semaphore_discount_danger": 0.0,
            }
        )
        line = self._create_line(95.0)
        self.assertTrue(line.semaphore_active)
        self.assertEqual(line.semaphore, "warning")
        self.assertEqual(line.semaphore_max_price_success, 100.0)
        self.assertEqual(line.semaphore_max_price_warning, 90.0)
        self.assertEqual(line.semaphore_max_price_danger, 80.0)

    def test_prepare_invoice_line_copies_semaphore(self):
        line = self._create_line(95.0)
        invoice_vals = line._prepare_invoice_line()
        self.assertEqual(invoice_vals["semaphore"], "warning")

    def _create_fixed_price_pricelist(self, name, price):
        return self.env["product.pricelist"].create(
            {
                "name": name,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": self.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "fixed_price": price,
                        },
                    )
                ],
            }
        )

    def test_pricelist_price_in_red_zone_does_not_block(self):
        """A line priced exactly at the pricelist must confirm even if the
        pricelist price falls in the red zone and has more decimals than the
        currency (regression: rounding made it look below the pricelist)."""
        # Danger threshold = 100 * (1 - 20%) = 80, so 79.9902 is in the red zone.
        pricelist = self._create_fixed_price_pricelist("Semaphore Pricelist", 79.9902)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "user_id": self.salesperson.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "name": self.product.name,
                "product_uom_qty": 1.0,
                "product_uom": self.product.uom_id.id,
            }
        )
        # Price comes straight from the pricelist (salesperson did not touch it).
        self.assertEqual(line.price_unit, 79.9902)
        self.assertTrue(line.price_below_semaphore)
        self.assertFalse(line._is_price_below_pricelist())
        # Must not raise for a regular salesperson.
        order.with_user(self.salesperson).action_confirm()
        self.assertEqual(order.state, "sale")

    def test_price_below_pricelist_blocks(self):
        """Lowering the price below the pricelist still blocks confirmation."""
        pricelist = self._create_fixed_price_pricelist(
            "Semaphore Pricelist Block", 79.9902
        )
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": pricelist.id}
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "name": self.product.name,
                "product_uom_qty": 1.0,
                "product_uom": self.product.uom_id.id,
                "price_unit": 70.0,
            }
        )
        self.assertTrue(line.price_below_semaphore)
        self.assertTrue(line._is_price_below_pricelist())
        with self.assertRaises(UserError):
            order.with_user(self.salesperson).action_confirm()
