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
                "semaphore_active": True,
                "semaphore_discount_success": 0.0,
                "semaphore_discount_warning": 10.0,
                "semaphore_discount_danger": 20.0,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

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
                "semaphore_active": True,
                "semaphore_discount_success": 5.0,
                "semaphore_discount_warning": 12.0,
                "semaphore_discount_danger": 20.0,
            }
        )
        self.assertTrue(self.product.semaphore_active)
        self.assertEqual(self.product.semaphore_discount_success, 5.0)
        self.assertEqual(self.product.semaphore_discount_warning, 12.0)
        self.assertEqual(self.product.semaphore_discount_danger, 20.0)
        self.assertTrue(template.semaphore_active)
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
        self.product.write(
            {
                "semaphore_active": False,
                "semaphore_discount_success": 99.0,
                "semaphore_discount_warning": 99.0,
                "semaphore_discount_danger": 99.0,
            }
        )
        data = self.product._get_semaphore_data()
        self.assertEqual(
            data,
            {"success": 0.0, "warning": 10.0, "danger": 20.0},
        )

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
            self.order.with_user(self.env.ref("base.user_demo")).action_confirm()

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
