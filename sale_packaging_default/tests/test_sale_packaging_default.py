# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import exceptions
from odoo.tests import Form

from odoo.addons.product.tests.common import ProductCommon


class SalePackagingDefaultCase(ProductCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].set_param(
            "sale_packaging_default.packaging_required", "0"
        )

        has_sales_field = "sales" in cls.env["uom.uom"]._fields

        uom_unit = cls.env.ref("uom.product_uom_unit")

        # Create UoMs
        cls.big_box = cls.env["uom.uom"].create(
            {
                "name": "Big box",
                "relative_uom_id": uom_unit.id,
                "relative_factor": 100,
            }
        )
        cls.dozen = cls.env["uom.uom"].create(
            {
                "name": "Dozen",
                "relative_uom_id": uom_unit.id,
                "relative_factor": 12,
            }
        )
        cls.small_box = cls.env["uom.uom"].create(
            {
                "name": "Small box",
                "relative_uom_id": uom_unit.id,
                "relative_factor": 6,
            }
        )

        if has_sales_field:
            cls.big_box.sales = True
            cls.dozen.sales = True
            cls.small_box.sales = True

        cls.product.uom_ids = [(6, 0, [cls.big_box.id, cls.dozen.id])]

        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Second Packaged Product",
                "type": "consu",
                "uom_ids": [(6, 0, [cls.small_box.id])],
            }
        )

        cls.product_without_packaging = cls.env["product.product"].create(
            {
                "name": "Product Without Packaging",
                "type": "consu",
            }
        )

    def test_default_packaging_sale_order(self):
        """Check is packaging usage in sale order."""
        so_f = Form(self.env["sale.order"])
        so_f.partner_id = self.partner
        with so_f.order_line.new() as line_f:
            line_f.product_id = self.product
            # Automatically set the default packaging (UoM)
            self.assertEqual(line_f.product_uom_id, self.big_box)

            # Change product, reset UoM
            line_f.product_id = self.product_without_packaging
            self.assertEqual(
                line_f.product_uom_id, self.product_without_packaging.uom_id
            )

    def test_product_change_between_packaged_products(self):
        """Check changing between two packaged products updates to default packaging."""
        so_f = Form(self.env["sale.order"])
        so_f.partner_id = self.partner
        with so_f.order_line.new() as line_f:
            line_f.product_id = self.product
            self.assertEqual(line_f.product_uom_id, self.big_box)

            # Change to second packaged product
            line_f.product_id = self.product_2
            self.assertEqual(line_f.product_uom_id, self.small_box)

    def test_has_packaging_available(self):
        """Check confirmation raises error if packaging required but invalid UoM set."""
        self.env["ir.config_parameter"].set_param(
            "sale_packaging_default.packaging_required", "1"
        )
        self.assertTrue(self.product.uom_ids)
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        with self.assertRaisesRegex(
            exceptions.UserError, "Some packaging is required but not set"
        ):
            sale.action_confirm()

    def test_required_packaging_error_on_sale_order_confirm(self):
        """Check error is raised when packaging is required
        but non-packaging UoM is used."""
        self.env["ir.config_parameter"].set_param(
            "sale_packaging_default.packaging_required", "1"
        )
        self.assertTrue(self.product.uom_ids)
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        self.assertTrue(sale.order_line[:1].is_packaging_required)
        with self.assertRaisesRegex(
            exceptions.UserError, "Some packaging is required but not set"
        ):
            sale.action_confirm()

    def test_has_not_packaging_available(self):
        """Check is_packaging_required is False when product has no packaging."""
        self.env["ir.config_parameter"].set_param(
            "sale_packaging_default.packaging_required", "1"
        )
        so_f = Form(self.env["sale.order"])
        so_f.partner_id = self.partner
        with so_f.order_line.new() as line:
            line.product_id = self.product_without_packaging
            self.assertFalse(line.is_packaging_required)
        so_f.save()

    def test_quantity_conversion_and_uom_change(self):
        """Check setting default packaging preserves/converts quantity."""
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                        },
                    )
                ],
            }
        )
        line = sale.order_line[0]
        self.assertEqual(line.product_uom_id, self.big_box)
        self.assertEqual(line.product_uom_qty, 5.0)

        # Change UoM to Dozen and verify line updates
        line.write({"product_uom_id": self.dozen.id})
        self.assertEqual(line.product_uom_id, self.dozen)
        self.assertEqual(line.product_uom_qty, 5.0)

    def test_action_confirm_success(self):
        """Confirm order successfully when valid packaging UoM is used."""
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_id": self.big_box.id,  # Uses a valid packaging
                        },
                    )
                ],
            }
        )
        res = sale.action_confirm()
        self.assertTrue(res)
        self.assertEqual(sale.state, "sale")

    def test_onchange_type_coverage(self):
        """Cover onchange helper with string, list, and falsy field names."""
        line = self.env["sale.order.line"].new()
        vals = {"product_id": self.product.id}
        res_str = line.onchange(vals, "product_id", {})
        self.assertIsInstance(res_str, dict)

        res_list = line.onchange(vals, ["product_id"], {})
        self.assertIsInstance(res_list, dict)

        res_falsy = line.onchange(vals, "", {})
        self.assertIsInstance(res_falsy, dict)

        # Cover empty product helpers
        self.assertFalse(line._get_sale_packagings())
        self.assertFalse(self.env["sale.order.line"]._get_default_packaging(None))
