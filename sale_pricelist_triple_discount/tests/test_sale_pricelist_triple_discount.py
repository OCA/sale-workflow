# Copyright 2022 Alberto Re - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class PricelistTripleDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})

        # A pricelist showing discounts to user and with three discounts set
        cls.pricelist1 = cls._create_price_list("Pricelist1", "without_discount")
        cls._create_pricelist_item(cls.pricelist1.id, 5.00, 10.00, 15.00)

        # A pricelist showing discounts to user and with two discounts set
        cls.pricelist2 = cls._create_price_list("Pricelist2", "without_discount")
        cls._create_pricelist_item(cls.pricelist2.id, 5.00, 10.00, 0.00)

        # A pricelist showing discounts to user and with only one discount set
        cls.pricelist3 = cls._create_price_list("Pricelist3", "without_discount")
        cls._create_pricelist_item(cls.pricelist3.id, 5.00, 0.00, 0.00)

        # Enable discount per SO line for current user
        cls.env.user.write(
            {
                "groups_id": [
                    (4, cls.env.ref("product.group_discount_per_so_line").id)
                ],
            }
        )

    @classmethod
    def _create_price_list(cls, name, policy):
        return cls.env["product.pricelist"].create(
            {
                "name": name,
                "active": True,
                "discount_policy": policy,
                "currency_id": cls.env.ref("base.EUR").id,
                "company_id": cls.env.user.company_id.id,
            }
        )

    @classmethod
    def _create_pricelist_item(cls, pricelist_id, discount1, discount2, discount3):
        return cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": pricelist_id,
                "applied_on": "3_global",
                "compute_price": "formula",
                "base": "list_price",
                "price_discount": discount1,
                "discount2": discount2,
                "discount3": discount3,
            }
        )

    def _create_sale_order(self, partner_id, pricelist_id):
        return self.env["sale.order"].create(
            {"partner_id": partner_id, "pricelist_id": pricelist_id}
        )

    def test_pricelist_without_discount_three_discounts(self):
        sale_order = self._create_sale_order(self.partner.id, self.pricelist1.id)
        product = self.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        sale_order_line = self.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "order_id": sale_order.id,
                "price_unit": 25.00,
                "product_uom_qty": 4,
            }
        )
        sale_order_line._onchange_discount()

        # Ensure price unit is not affected by the discount (without_discount)
        self.assertEqual(sale_order_line.price_unit, 25.00)

        # Ensure discounts are correctly displayed in the order line(s)
        self.assertEqual(sale_order_line.discount, 5.00)
        self.assertEqual(sale_order_line.discount2, 10.00)
        self.assertEqual(sale_order_line.discount3, 15.00)

        # Ensure line(s) subtotal is calculated properly
        self.assertEqual(sale_order_line.price_subtotal, 72.68)

    def test_pricelist_without_discount_two_discounts(self):
        sale_order = self._create_sale_order(self.partner.id, self.pricelist2.id)
        product = self.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        sale_order_line = self.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "order_id": sale_order.id,
                "price_unit": 25.00,
                "product_uom_qty": 4,
            }
        )
        sale_order_line._onchange_discount()

        # Ensure price unit is not affected by the discount (without_discount)
        self.assertEqual(sale_order_line.price_unit, 25.00)

        # Ensure discounts are correctly displayed in the order line(s)
        self.assertEqual(sale_order_line.discount, 5.00)
        self.assertEqual(sale_order_line.discount2, 10.00)
        self.assertEqual(sale_order_line.discount3, 0.00)

        # Ensure line(s) subtotal is calculated properly
        self.assertEqual(sale_order_line.price_subtotal, 85.5)

    def test_pricelist_without_discount_one_discounts(self):
        sale_order = self._create_sale_order(self.partner.id, self.pricelist3.id)
        product = self.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        sale_order_line = self.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "order_id": sale_order.id,
                "price_unit": 25.00,
                "product_uom_qty": 4,
            }
        )
        sale_order_line._onchange_discount()

        # Ensure price unit is not affected by the discount (without_discount)
        self.assertEqual(sale_order_line.price_unit, 25.00)

        # Ensure discounts are correctly displayed in the order line(s)
        self.assertEqual(sale_order_line.discount, 5.00)
        self.assertEqual(sale_order_line.discount2, 0.00)
        self.assertEqual(sale_order_line.discount3, 0.00)

        # Ensure line(s) subtotal is calculated properly
        self.assertEqual(sale_order_line.price_subtotal, 95.0)
