from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestSaleOrderTypeFilterProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.sale_type_a = cls.env["sale.order.type"].create(
            {
                "name": "Type A",
                "company_id": cls.company.id,
            }
        )
        cls.sale_type_b = cls.env["sale.order.type"].create(
            {
                "name": "Type B",
                "company_id": cls.company.id,
            }
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "sale_ok": True,
                "sale_order_type_ids": [(6, 0, cls.sale_type_a.ids)],
            }
        )
        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Attribute",
                "create_variant": "always",
            }
        )
        cls.attribute_value_a = cls.env["product.attribute.value"].create(
            {
                "name": "Variant A",
                "attribute_id": cls.attribute.id,
            }
        )
        cls.attribute_value_b = cls.env["product.attribute.value"].create(
            {
                "name": "Variant B",
                "attribute_id": cls.attribute.id,
            }
        )
        cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.product_tmpl.id,
                "attribute_id": cls.attribute.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.attribute_value_a.id,
                            cls.attribute_value_b.id,
                        ],
                    )
                ],
            }
        )
        cls.variant_a = cls.product_tmpl.product_variant_ids.filtered(
            lambda product: product.product_template_attribute_value_ids.name
            == "Variant A"
        )
        cls.variant_b = cls.product_tmpl.product_variant_ids.filtered(
            lambda product: product.product_template_attribute_value_ids.name
            == "Variant B"
        )
        cls.variant_a.variant_sale_order_type_ids = cls.sale_type_a
        cls.variant_b.variant_sale_order_type_ids = cls.sale_type_b
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )

    def test_product_without_variants(self):
        product_tmpl = self.env["product.template"].create(
            {
                "name": "Product Without Variants",
                "sale_ok": True,
                "sale_order_type_ids": [(6, 0, self.sale_type_a.ids)],
            }
        )
        product = product_tmpl.product_variant_id
        self.assertEqual(
            product._get_allowed_sale_order_types(),
            self.sale_type_a,
        )

    def test_product_with_variants_uses_template_sale_order_types(self):
        self.variant_a.variant_sale_order_type_ids = False
        self.variant_b.variant_sale_order_type_ids = False
        self.assertEqual(
            self.variant_a._get_allowed_sale_order_types(),
            self.sale_type_a,
        )
        self.assertEqual(
            self.variant_b._get_allowed_sale_order_types(),
            self.sale_type_a,
        )

    def test_product_variant_sale_order_types_override_template(self):
        self.variant_a.variant_sale_order_type_ids = self.sale_type_b
        self.assertEqual(
            self.variant_a._get_allowed_sale_order_types(),
            self.sale_type_b,
        )

    def test_archived_variant_keeps_sale_order_type_restriction(self):
        self.variant_a.variant_sale_order_type_ids = self.sale_type_b
        self.variant_a.active = False
        self.assertFalse(self.variant_a.active)
        self.assertEqual(
            self.variant_a._get_allowed_sale_order_types(),
            self.sale_type_b,
        )

    def test_archived_variant_is_not_considered_available(self):
        self.variant_b.active = False
        active_variants = self.product_tmpl.product_variant_ids
        self.assertIn(self.variant_a, active_variants)
        self.assertNotIn(self.variant_b, active_variants)

    def test_product_without_sale_order_type_restriction(self):
        product_tmpl = self.env["product.template"].create(
            {
                "name": "Unrestricted Product",
                "sale_ok": True,
            }
        )
        product = product_tmpl.product_variant_id
        self.assertFalse(product._get_allowed_sale_order_types())

    def test_sale_order_line_allowed_product(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "type_id": self.sale_type_a.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.variant_a.id,
                "product_uom_qty": 1,
            }
        )
        self.assertEqual(line.product_id, self.variant_a)

    def test_sale_order_line_invalid_product(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "type_id": self.sale_type_a.id,
            }
        )
        with self.assertRaises(exceptions.ValidationError):
            self.env["sale.order.line"].create(
                {
                    "order_id": order.id,
                    "product_id": self.variant_b.id,
                    "product_uom_qty": 1,
                }
            )

    def test_prevent_sale_order_type_change_with_invalid_product(self):
        self.company.sale_order_type_invalid_product_action = "prevent"
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "type_id": self.sale_type_a.id,
            }
        )
        self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.variant_a.id,
                "product_uom_qty": 1,
            }
        )
        with self.assertRaises(exceptions.UserError):
            order.write({"type_id": self.sale_type_b.id})
        self.assertEqual(order.type_id, self.sale_type_a)

    def test_remove_invalid_lines_on_sale_order_type_change(self):
        self.company.sale_order_type_invalid_product_action = "remove"
        self.variant_a.variant_sale_order_type_ids = self.sale_type_a | self.sale_type_b
        self.variant_b.variant_sale_order_type_ids = self.sale_type_a
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "type_id": self.sale_type_a.id,
            }
        )
        valid_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.variant_a.id,
                "product_uom_qty": 1,
            }
        )
        invalid_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.variant_b.id,
                "product_uom_qty": 1,
            }
        )
        order.write({"type_id": self.sale_type_b.id})
        self.assertEqual(order.type_id, self.sale_type_b)
        self.assertIn(valid_line, order.order_line)
        self.assertNotIn(invalid_line, order.order_line)
        self.assertFalse(invalid_line.exists())

    def test_sale_order_type_change_with_all_products_allowed(self):
        self.variant_a.variant_sale_order_type_ids = self.sale_type_a | self.sale_type_b
        self.variant_b.variant_sale_order_type_ids = self.sale_type_a | self.sale_type_b
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "type_id": self.sale_type_a.id,
            }
        )
        line_a = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.variant_a.id,
                "product_uom_qty": 1,
            }
        )
        line_b = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.variant_b.id,
                "product_uom_qty": 1,
            }
        )
        order.write({"type_id": self.sale_type_b.id})
        self.assertEqual(order.type_id, self.sale_type_b)
        self.assertIn(line_a, order.order_line)
        self.assertIn(line_b, order.order_line)
        self.assertEqual(len(order.order_line), 2)

    def test_sale_order_line_product_without_restrictions(self):
        product_tmpl = self.env["product.template"].create(
            {
                "name": "Unrestricted Product",
                "sale_ok": True,
            }
        )
        product = product_tmpl.product_variant_id
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "type_id": self.sale_type_a.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": product.id,
                "product_uom_qty": 1,
            }
        )
        order.write({"type_id": self.sale_type_b.id})
        self.assertEqual(order.type_id, self.sale_type_b)
        self.assertIn(line, order.order_line)
        self.assertTrue(line.exists())

    def test_variant_sale_order_type_multicompany(self):
        company_b = self.env["res.company"].create(
            {
                "name": "Company B",
            }
        )
        sale_type_b_company = self.env["sale.order.type"].create(
            {
                "name": "Company B Type",
                "company_id": company_b.id,
            }
        )
        self.variant_a.variant_sale_order_type_ids = sale_type_b_company
        variant = self.variant_a.with_context(allowed_company_ids=[self.company.id])
        self.assertEqual(
            variant._get_allowed_sale_order_types(),
            sale_type_b_company,
        )

    def test_multicompany_variant_is_not_unrestricted(self):
        company_b = self.env["res.company"].create(
            {
                "name": "Company B",
            }
        )
        sale_type_b_company = self.env["sale.order.type"].create(
            {
                "name": "Company B Type",
                "company_id": company_b.id,
            }
        )
        self.variant_a.variant_sale_order_type_ids = sale_type_b_company
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "type_id": self.sale_type_a.id,
            }
        )
        with self.assertRaises(exceptions.ValidationError):
            self.env["sale.order.line"].create(
                {
                    "order_id": order.id,
                    "product_id": self.variant_a.id,
                    "product_uom_qty": 1,
                }
            )
