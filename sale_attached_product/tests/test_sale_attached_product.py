# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common


class TestSaleAttachedProduct(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # No need for tracking and we scratch some seconds
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Mr. Odoo", "property_product_pricelist": cls.pricelist.id}
        )
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Test 1", "sale_ok": True, "list_price": 50}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test 2", "sale_ok": False, "list_price": 60}
        )
        cls.product_3 = cls.env["product.product"].create(
            {"name": "Test 3", "sale_ok": False, "list_price": 70}
        )
        cls.product_4 = cls.env["product.product"].create(
            {"name": "Test 4", "sale_ok": False, "list_price": 80}
        )
        cls.product_5 = cls.env["product.product"].create(
            {"name": "Test 4", "sale_ok": False, "list_price": 80}
        )
        cls.product_1.product_tmpl_id.attached_product_ids = (
            cls.product_2 + cls.product_3
        )
        # We'll be using this sale order
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        cls.sale = sale_form.save()

    def _add_product(self, sale, product, qty=1):
        """Auxiliar method to quickly add products to a sale order"""
        sale_form = Form(sale)
        with sale_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = qty
        sale_form.save()

    def _get_attached_lines(self, sale):
        return sale.order_line.filtered("is_attached_line")

    def test_01_attach_product_modifiable(self):
        """Every time we add a product with attached products we'll adding extra lines
        automatically"""
        # When we add a product with attached products defined on it the module will add
        # as many lines as attached products
        self._add_product(self.sale, self.product_1)
        product_1_line = self.sale.order_line.filtered(
            lambda x: x.product_id == self.product_1
        )
        self.assertEqual(
            len(self.sale.order_line),
            3,
            "Two extra lines should have been added automatically",
        )
        self.assertEqual(
            self._get_attached_lines(self.sale).product_id,
            self.product_1.product_tmpl_id.attached_product_ids,
            "The attached lines products should correspond with those defined in the "
            "product",
        )
        # Once added, we can edit the lines independetly
        product_1_line.product_uom_qty = 3
        self.assertTrue(
            all(x.product_uom_qty == 1 for x in self._get_attached_lines(self.sale))
        )
        # We can delete attached lines in this mode
        self.sale.order_line.filtered(lambda x: x.product_id == self.product_2).unlink()
        self.assertEqual(
            len(self.sale.order_line), 2, "The line should stay removed",
        )
        # Removing the main line will kill the optional ones anyway
        product_1_line.unlink()
        self.assertFalse(
            self._get_attached_lines(self.sale), "There should be no attached lines"
        )

    def test_02_attach_product_auto_update(self):
        """Every time we add a product with attached products we'll adding extra lines
        automatically. Those lines will be persistent"""
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_attached_product.auto_update_attached_lines", True
        )
        # When we add a product with attached products defined on it the module will add
        # as many lines as attached products
        self._add_product(self.sale, self.product_1)
        product_1_line = self.sale.order_line.filtered(
            lambda x: x.product_id == self.product_1
        )
        self.assertEqual(
            len(self.sale.order_line),
            3,
            "Two extra lines should have been added automatically",
        )
        self.assertEqual(
            self._get_attached_lines(self.sale).product_id,
            self.product_1.product_tmpl_id.attached_product_ids,
            "The attached lines products should correspond with those defined in the "
            "product",
        )
        # When we change the line quantity, the lines change theirs as well
        product_1_line.product_uom_qty = 3
        self.assertTrue(
            all(
                x.product_uom_qty == product_1_line.product_uom_qty
                for x in self._get_attached_lines(self.sale)
            )
        )
        # When we delete an attached line, the module will recreate it to keep the
        # attached lines consitency
        self.sale.order_line.filtered(lambda x: x.product_id == self.product_2).unlink()
        self.assertEqual(
            len(self.sale.order_line), 3, "The removed line should be recreated",
        )
        # Adding another product doesn't have any effect on the rest
        self._add_product(self.sale, self.product_4)
        self.assertEqual(
            len(self.sale.order_line),
            4,
            "Product 4 doesn't have any attached products",
        )
        # Changing the main line product will invalidate the attached lines
        product_1_line.product_id = self.product_5
        self.assertEqual(
            len(self.sale.order_line),
            2,
            "The new product doesn't have any attached products",
        )
        self.assertFalse(
            self._get_attached_lines(self.sale), "There should be no attached lines"
        )
        # If we change it back, the attached lines will be added back as well
        product_1_line.product_id = self.product_1
        self.assertEqual(
            len(self.sale.order_line), 4, "The attached lines should be added again",
        )
        self.assertEqual(
            self._get_attached_lines(self.sale).product_id,
            self.product_1.product_tmpl_id.attached_product_ids,
            "The attached lines products should correspond with those defined in the "
            "product",
        )
        # Removing the main line, removes the attached lines
        product_1_line.unlink()
        self.assertFalse(
            self._get_attached_lines(self.sale), "There should be no attached lines"
        )
