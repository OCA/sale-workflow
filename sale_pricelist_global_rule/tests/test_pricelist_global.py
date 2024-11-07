from odoo.addons.base.tests.common import TransactionCase


class TestPricelistGlobal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductAttribute = cls.env["product.attribute"]
        cls.ProductAttributeValue = cls.env["product.attribute.value"]
        cls.Product = cls.env["product.product"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductTemplateAttribute = cls.env["product.template.attribute.line"]
        cls.ProductCateg = cls.env["product.category"]
        cls.Pricelist = cls.env["product.pricelist"]
        cls.PricelistItem = cls.env["product.pricelist.item"]
        cls.Partner = cls.env["res.partner"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.attr_size = cls.ProductAttribute.create(
            {"name": "sale_pricelist_global_rule Size", "sequence": 1}
        )
        cls.attr_color = cls.ProductAttribute.create(
            {"name": "sale_pricelist_global_rule Color", "sequence": 2}
        )
        cls.size_m = cls.ProductAttributeValue.create(
            {
                "name": "M",
                "attribute_id": cls.attr_size.id,
                "sequence": 1,
            }
        )
        cls.size_l = cls.ProductAttributeValue.create(
            {
                "name": "L",
                "attribute_id": cls.attr_size.id,
                "sequence": 2,
            }
        )
        cls.color_red = cls.ProductAttributeValue.create(
            {
                "name": "Red",
                "attribute_id": cls.attr_color.id,
                "sequence": 1,
            }
        )
        cls.color_black = cls.ProductAttributeValue.create(
            {
                "name": "Black",
                "attribute_id": cls.attr_color.id,
                "sequence": 2,
            }
        )
        cls.categ_1 = cls.ProductCateg.create({"name": "Categ 1"})
        cls.categ_2 = cls.ProductCateg.create({"name": "Categ 2"})
        cls.t_shirt = cls.ProductTemplate.create(
            {"name": "T-Shirt", "list_price": 100, "categ_id": cls.categ_1.id}
        )
        cls.template_attr_sizes = cls.ProductTemplateAttribute.create(
            {
                "product_tmpl_id": cls.t_shirt.id,
                "attribute_id": cls.attr_size.id,
                "value_ids": [(6, 0, [cls.size_m.id, cls.size_l.id])],
            }
        )
        cls.template_attr_colors = cls.ProductTemplateAttribute.create(
            {
                "product_tmpl_id": cls.t_shirt.id,
                "attribute_id": cls.attr_color.id,
                "value_ids": [(6, 0, [cls.color_red.id, cls.color_black.id])],
            }
        )
        cls.template_attr_size_m = cls.template_attr_sizes.product_template_value_ids[0]
        cls.template_attr_size_l = cls.template_attr_sizes.product_template_value_ids[1]
        cls.template_attr_color_red = (
            cls.template_attr_colors.product_template_value_ids[0]
        )
        cls.template_attr_color_black = (
            cls.template_attr_colors.product_template_value_ids[1]
        )
        cls.t_shirt_m_red = cls.t_shirt._get_variant_for_combination(
            cls.template_attr_size_m + cls.template_attr_color_red
        )
        cls.t_shirt_m_black = cls.t_shirt._get_variant_for_combination(
            cls.template_attr_size_m + cls.template_attr_color_black
        )
        cls.product_2 = cls.Product.create(
            {"name": "Product 2", "list_price": 200, "categ_id": cls.categ_1.id}
        )
        cls.product_3 = cls.Product.create(
            {"name": "Product 3", "list_price": 300, "categ_id": cls.categ_2.id}
        )
        cls.pricelist_base = cls.Pricelist.create({"name": "Base Pricelist"})
        cls.pricelist_global = cls.Pricelist.create({"name": "Global Pricelist"})
        cls.pricelist_item_by_product = cls.PricelistItem.create(
            {
                "pricelist_id": cls.pricelist_global.id,
                "applied_on": "4_global_product_template",
                "global_product_tmpl_id": cls.t_shirt.id,
                "compute_price": "percentage",
                "percent_price": 10,
                "min_quantity": 15,
            }
        )
        cls.pricelist_item_by_categ = cls.PricelistItem.create(
            {
                "pricelist_id": cls.pricelist_global.id,
                "applied_on": "5_global_product_category",
                "global_categ_id": cls.categ_1.id,
                "compute_price": "percentage",
                "percent_price": 10,
                "min_quantity": 20,
            }
        )
        cls.pricelist_item_base = cls.PricelistItem.create(
            {
                "pricelist_id": cls.pricelist_base.id,
                "applied_on": "1_product",
                "product_tmpl_id": cls.t_shirt.id,
                "compute_price": "percentage",
                "percent_price": 20,
                "min_quantity": 5,
            }
        )
        cls.partner_1 = cls.Partner.create({"name": "Partner 1"})
        cls.partner_2 = cls.Partner.create({"name": "Partner 2"})
        cls.sale_order1 = cls.SaleOrder.create(
            {
                "partner_id": cls.partner_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "pricelist_id": cls.pricelist_global.id,
            }
        )
        cls.sale_line_m_red = cls.SaleOrderLine.create(
            {
                "order_id": cls.sale_order1.id,
                "product_id": cls.t_shirt_m_red.id,
                "product_uom_qty": 1,
                "price_unit": 100,
            }
        )
        cls.sale_line_m_black = cls.SaleOrderLine.create(
            {
                "order_id": cls.sale_order1.id,
                "product_id": cls.t_shirt_m_black.id,
                "product_uom_qty": 1,
                "price_unit": 100,
            }
        )
        cls.sale_line_2 = cls.SaleOrderLine.create(
            {
                "order_id": cls.sale_order1.id,
                "product_id": cls.product_2.id,
                "product_uom_qty": 1,
                "price_unit": 200,
            }
        )
        cls.sale_line_3 = cls.SaleOrderLine.create(
            {
                "order_id": cls.sale_order1.id,
                "product_id": cls.product_3.id,
                "product_uom_qty": 1,
                "price_unit": 300,
            }
        )
        cls.env.user.groups_id += cls.env.ref("product.group_discount_per_so_line")

    def test_01_by_product_less_min_quantity(self):
        """
        Verify that the total quantity (9) is less than the minimum quantity (10).
        product_m_red: qty=4, price=100
        product_m_black: qty=5, price=100
        product_2: qty=1, price=200
        product_3: qty=1, price=300
        """
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 5
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_02_by_product_fixed_price(self):
        """
        Only product_m_red and product_m_black have fixed prices
        After applying the global pricelist: min_quantity=15, Total qty=15
        product_m_red: qty=7, price=50(fixed)
        product_m_black: qty=8, price=50(fixed)
        product_2: qty=1, price=200(unchanged)
        product_3: qty=1, price=300(unchanged)
        """
        self.pricelist_item_by_product.write(
            {
                "compute_price": "fixed",
                "fixed_price": 50,
            }
        )
        self.sale_line_m_red.product_uom_qty = 7
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 50)
        self.assertEqual(self.sale_line_m_black.price_unit, 50)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_03_by_product_discount(self):
        """
        Only product_m_red and product_m_black have 10% discount
        After apply the global pricelist: min_quantity=15, Total qty=15
        product_m_red: qty=7, price=90
        product_m_black: qty=8, price=90
        product_2: qty=1, price=200(unchanged)
        product_3: qty=1, price=300(unchanged)
        """
        self.sale_line_m_red.product_uom_qty = 7
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 90)
        self.assertEqual(self.sale_line_m_black.price_unit, 90)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_04_by_product_formula(self):
        """
        Only product_m_red and product_m_black have 20% discount
        After applying the global pricelist: min_quantity=15, Total qty=15
        product_m_red: qty=7, price=80
        product_m_black: qty=8, price=80
        product_2: qty=1, price=200(unchanged)
        product_3: qty=1, price=300(unchanged)
        """
        self.pricelist_item_by_product.write(
            {
                "compute_price": "formula",
                "price_discount": 20,
            }
        )
        self.sale_line_m_red.product_uom_qty = 7
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 80)
        self.assertEqual(self.sale_line_m_black.price_unit, 80)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # with surcharge(+)
        self.pricelist_item_by_product.write({"price_surcharge": 5})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 85)
        self.assertEqual(self.sale_line_m_black.price_unit, 85)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # with surcharge(-)
        self.pricelist_item_by_product.write({"price_surcharge": -5})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 75)
        self.assertEqual(self.sale_line_m_black.price_unit, 75)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_05_by_product_base_other_pricelist_normal(self):
        """
        Base pricelist offers a 20% discount on t_shirt with min_quantity=5
        Global pricelist offers a 10% discount on product_m_red with min_quantity=15
        Case 1:
            - Total quantity=8.
            - Global pricelist does not apply.
            - Base pricelist is not evaluated.
        Case 2:
            - Total qty=15
            - Base pricelist:
                - Applies only to sale_line_m_black(quantity=11)
            - Global pricelist:
                - sale_line_m_red = 100 * 10% discount = 90
                - sale_line_m_black:
                    - Base price  = 100 * 20% discount (from base pricelist=80)
                    - Final price = 80 * 10% discount = 72
        Case 3:
            - Total qty=16
            - Base pricelist:
                - Applies to both sale_line_m_red and sale_line_m_black (both with quantity=8)
            - Global pricelist:
                - Base price  = 100 * 20% discount (from base pricelist=80)
                - Final price = 80 * 10% discount = 72
        """
        self.pricelist_item_by_product.write(
            {
                "base": "pricelist",
                "base_pricelist_id": self.pricelist_base.id,
            }
        )
        # case 1
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 4
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 2
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 11
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 90)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 3
        self.sale_line_m_red.product_uom_qty = 8
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 72)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_06_by_product_base_other_pricelist_global(self):
        """
        base pricelist have 20% discount for t_shirt with min_quantity=5
        global pricelist have 10% discount for product_m_red with min_quantity=15
        Case 1: Total qty=8, not apply global pricelist, no eval base pricelist
        Case 2: Total qty=16, apply global pricelist
        - base pricelist:
            applicable for sale_line_m_red and sale_line_m_black (total quantity=16)
        - global pricelist:
            - base_price = 100 * 20% discount (from base pricelist)
            - final_price = 80 * 10% discount = 72

        """
        self.pricelist_item_base.write(
            {
                "applied_on": "4_global_product_template",
                "global_product_tmpl_id": self.t_shirt.id,
            }
        )
        self.pricelist_item_by_product.write(
            {
                "base": "pricelist",
                "base_pricelist_id": self.pricelist_base.id,
            }
        )
        # case 1
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 4
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 2
        self.sale_line_m_red.product_uom_qty = 8
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 72)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_11_by_categ_less_min_quantity(self):
        """
        Verify that the total quantity (19) is less than the minimum quantity (20).
        product_m_red: qty=4, price=100
        product_m_black: qty=5, price=100
        product_2: qty=10, price=200
        product_3: qty=10, price=300
        """
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 5
        self.sale_line_2.product_uom_qty = 10
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_12_by_categ_fixed_price(self):
        """
        Only product_m_red and product_m_black, product_2 have fixed prices.
        After applying the global pricelist: min_quantity=20, Total qty=24
        product_m_red: qty=4, price=50(fixed)
        product_m_black: qty=5, price=50(fixed)
        product_2: qty=15, price=50(fixed)
        product_3: qty=10, price=300(unchanged)
        """
        self.pricelist_item_by_categ.write(
            {
                "compute_price": "fixed",
                "fixed_price": 50,
            }
        )
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 5
        self.sale_line_2.product_uom_qty = 15
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 50)
        self.assertEqual(self.sale_line_m_black.price_unit, 50)
        self.assertEqual(self.sale_line_2.price_unit, 50)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_13_by_categ_discount(self):
        """
        Only product_m_red and product_m_black, product_2 have 10% discount
        After apply global pricelist: min_quantity=20, Total qty=24
        product_m_red: qty=4, price=90
        product_m_black: qty=5, price=90
        product_2: qty=15, price=180
        product_3: qty=10, price=300(unchanged)
        """
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 5
        self.sale_line_2.product_uom_qty = 15
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 90)
        self.assertEqual(self.sale_line_m_black.price_unit, 90)
        self.assertEqual(self.sale_line_2.price_unit, 180)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_14_by_categ_formula(self):
        """
        Only product_m_red and product_m_black, product_2 have 20% discount
        After apply global pricelist: min_quantity=20, Total qty=24
        product_m_red: qty=4, price=80
        product_m_black: qty=5, price=80
        product_2: qty=15, price=160
        product_3: qty=10, price=300(unchanged)
        """
        self.pricelist_item_by_categ.write(
            {
                "compute_price": "formula",
                "price_discount": 20,
            }
        )
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 5
        self.sale_line_2.product_uom_qty = 15
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 80)
        self.assertEqual(self.sale_line_m_black.price_unit, 80)
        self.assertEqual(self.sale_line_2.price_unit, 160)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # with surcharge(+)
        self.pricelist_item_by_categ.write({"price_surcharge": 5})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 85)
        self.assertEqual(self.sale_line_m_black.price_unit, 85)
        self.assertEqual(self.sale_line_2.price_unit, 165)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # with surcharge(-)
        self.pricelist_item_by_categ.write({"price_surcharge": -5})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 75)
        self.assertEqual(self.sale_line_m_black.price_unit, 75)
        self.assertEqual(self.sale_line_2.price_unit, 155)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_15_by_categ_base_other_pricelist_normal(self):
        """
        base pricelist offers a 20% discount on t_shirt with min_quantity=5
        global pricelist offers a 10% discount on categ1 with min_quantity=20
        Case 1:
            - Total qty=9
            - Global pricelist does not apply.
            - Base pricelist is not evaluated.
        Case 2:
            - Total qty=20
            - Base pricelist:
                - applicable only to sale_line_m_black(quantity=8)
            - Global pricelist:
                - sale_line_m_red = 100 * 10% discount = 90
                - sale_line_2 = 200 * 10% discount = 180
                - sale_line_m_black:
                    - base_price = 100 * 20% discount (from base pricelist)
                    - final_price = 80 * 10% discount = 72
        Case 3:
            - Total qty=22
            - Base pricelist:
                applicable on sale_line_m_red (with quantity=6)
                applicable on sale_line_m_black (with quantity=8)
                applicable on sale_line_2 (quantity=8)
            - Global pricelist:
                - base_price = 100 * 20% discount (from base pricelist)
                - final_price = 80 * 10% discount = 72
        """
        self.pricelist_item_by_categ.write(
            {
                "base": "pricelist",
                "base_pricelist_id": self.pricelist_base.id,
            }
        )
        # case 1
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 4
        self.sale_line_2.product_uom_qty = 1
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 2
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_line_2.product_uom_qty = 8
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 90)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_2.price_unit, 180)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 3
        self.sale_line_m_red.product_uom_qty = 6
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_line_2.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 72)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_2.price_unit, 180)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_16_by_categ_base_other_pricelist_global(self):
        """
        Base pricelist offers a 20% discount for t_shirt with min_quantity=5
        global pricelist offers a 10% discount for categ1 with min_quantity=20
        Case 1:
            - Total quantity=9.
            - Global pricelist does not apply.
            - Base pricelist is not evaluated.
        Case 2:
            - Total qty=21
            - Base pricelist:
                - Applicable on sale_line_m_red and sale_line_m_black (both with quantity=7)
                - Applicable on sale_line_2 (quantity=7)
            - Global pricelist:
                - Applicable on sale_line_m_red and sale_line_m_black
                    - Base price = 100 * 20% discount (from Base pricelist)
                    - Final price = 80 * 10% discount = 72
                - Applicable on sale_line_2:
                    - Base price = 200 * 20% discount (from Base pricelist)
                    - Final price = 160 * 10% discount = 144
        """
        self.pricelist_item_base.write(
            {
                "applied_on": "5_global_product_category",
                "global_categ_id": self.categ_1.id,
            }
        )
        self.pricelist_item_by_categ.write(
            {
                "base": "pricelist",
                "base_pricelist_id": self.pricelist_base.id,
            }
        )
        # case 1
        self.sale_line_m_red.product_uom_qty = 4
        self.sale_line_m_black.product_uom_qty = 4
        self.sale_line_2.product_uom_qty = 1
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 2
        self.sale_line_m_red.product_uom_qty = 7
        self.sale_line_m_black.product_uom_qty = 7
        self.sale_line_2.product_uom_qty = 7
        self.sale_line_3.product_uom_qty = 10
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 72)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_2.price_unit, 144)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_pricelist_by_dates(self):
        """
        Case 1: Not available due to date_start
        Case 2: Not available due to date_end
        Case 3: 10% discount applied to product_m_red and product_m_black
        """
        self.pricelist_item_by_product.write(
            {
                "date_start": "2024-12-31 00:00:00",
                "date_end": "2024-12-31 23:59:59",
            }
        )
        # case 1
        self.sale_order1.date_order = "2024-12-30 23:59:59"
        self.sale_line_m_red.product_uom_qty = 8
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 2
        self.sale_order1.date_order = "2025-01-01 00:00:00"
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 3
        self.sale_order1.date_order = "2024-12-31 00:00:00"
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 90)
        self.assertEqual(self.sale_line_m_black.price_unit, 90)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_pricelist_by_uom(self):
        """
        Global pricelist 10% discount for t_shirt with min_quantity=15
        Case 1:
            - Total qty=2 Units(global pricelist not applied)
            - product_m_red: uom=Units, qty=1, price=100
            - product_m_black: uom=Units, qty=1, price=100
        Case 2:
            - Total qty=13 Units(global pricelist not applied)
            - product_m_red: uom=Dozen, qty=1, price=100
            - product_m_black: uom=Units, qty=1, price=100
        Case 3:
            - Total qty=18 Units(global pricelist applied)
            - product_m_red: uom=Dozen, qty=1, price=90
            - product_m_black: uom=Units, qty=6, price=90
        """
        # case 1
        self.sale_line_m_red.product_uom_qty = 1
        self.sale_line_m_black.product_uom_qty = 1
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 2
        self.sale_line_m_red.product_uom_qty = 1
        self.sale_line_m_red.product_uom = self.env.ref("uom.product_uom_dozen")
        self.sale_line_m_black.product_uom_qty = 1
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        # case 3
        self.sale_line_m_red.product_uom_qty = 1
        self.sale_line_m_red.product_uom = self.env.ref("uom.product_uom_dozen")
        self.sale_line_m_black.product_uom_qty = 6
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 90)
        self.assertEqual(self.sale_line_m_black.price_unit, 90)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_3.price_unit, 300)

    def test_pricelist_visible_discount(self):
        """
        Base pricelist: 20% discount for t_shirt with min_quantity=5
        Global pricelist: 10% discount for t_shirt with min_quantity=15
        All cases:
            - product_m_red: qty=8, applies global pricelist(total 16)
            - product_m_black: qty=8, applies global pricelist(total 16)
            - product_2: qty=1, price=200, discount=0. No pricelist applied
            - product_3: qty=1, price=300, discount=0. No pricelist applied
        Case 1:
            - Based on list price
            - Global pricelist discount policy: with_discount
            - product_m_red: price=90, discount=0
            - product_m_black: price=90, discount=0
        Case 2:
            - Based on list price
            - Global pricelist discount policy: without_discount
            - product_m_red: price=100, discount=10
            - product_m_black: price=100, discount=10
        Case 3:
            - Based on other pricelist
            - Global pricelist discount policy: with_discount
            - base pricelist discount_policywith_discount
            - product_m_red: price=72, discount=0
            - product_m_black: price=72, discount=0
        Case 4:
            - Based on other pricelist
            - Global pricelist discount policy: without_discount
            - base pricelist discount_policy: with_discount
            - product_m_red: price=80, discount=10
            - product_m_black: price=80, discount=10
        Case 5:
            - Based on other pricelist
            - Global pricelist discount policy: with_discount
            - base pricelist discount_policy: without_discount
            - product_m_red: price=80, discount=10
            - product_m_black: price=80, discount=10
        Case 6:
            - Based on other pricelist
            - Global pricelist discount policy: without_discount
            - base pricelist discount_policy: without_discount
            - product_m_red: price=100, discount=28
            - product_m_black: price=100, discount=28
        """
        # case 1
        self.pricelist_global.write({"discount_policy": "with_discount"})
        self.sale_line_m_red.product_uom_qty = 8
        self.sale_line_m_black.product_uom_qty = 8
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 90)
        self.assertEqual(self.sale_line_m_red.discount, 0)
        self.assertEqual(self.sale_line_m_black.price_unit, 90)
        self.assertEqual(self.sale_line_m_black.discount, 0)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_2.discount, 0)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        self.assertEqual(self.sale_line_3.discount, 0)
        # case 2
        self.pricelist_global.write({"discount_policy": "without_discount"})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_red.discount, 10)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.discount, 10)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_2.discount, 0)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        self.assertEqual(self.sale_line_3.discount, 0)
        # case 3
        self.pricelist_item_by_product.write(
            {
                "base": "pricelist",
                "base_pricelist_id": self.pricelist_base.id,
            }
        )
        self.pricelist_global.write({"discount_policy": "with_discount"})
        self.pricelist_base.write({"discount_policy": "with_discount"})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 72)
        self.assertEqual(self.sale_line_m_red.discount, 0)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_m_black.discount, 0)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_2.discount, 0)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        self.assertEqual(self.sale_line_3.discount, 0)
        # case 4
        self.pricelist_global.write({"discount_policy": "without_discount"})
        self.pricelist_base.write({"discount_policy": "with_discount"})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 80)
        self.assertEqual(self.sale_line_m_red.discount, 10)
        self.assertEqual(self.sale_line_m_black.price_unit, 80)
        self.assertEqual(self.sale_line_m_black.discount, 10)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_2.discount, 0)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        self.assertEqual(self.sale_line_3.discount, 0)
        # case 5
        self.pricelist_global.write({"discount_policy": "with_discount"})
        self.pricelist_base.write({"discount_policy": "without_discount"})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 72)
        self.assertEqual(self.sale_line_m_red.discount, 0)
        self.assertEqual(self.sale_line_m_black.price_unit, 72)
        self.assertEqual(self.sale_line_m_black.discount, 0)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_2.discount, 0)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        self.assertEqual(self.sale_line_3.discount, 0)
        # case 6
        self.pricelist_global.write({"discount_policy": "without_discount"})
        self.pricelist_base.write({"discount_policy": "without_discount"})
        self.sale_order1.button_compute_pricelist_global_rule()
        self.assertEqual(self.sale_line_m_red.price_unit, 100)
        self.assertEqual(self.sale_line_m_red.discount, 28)
        self.assertEqual(self.sale_line_m_black.price_unit, 100)
        self.assertEqual(self.sale_line_m_black.discount, 28)
        self.assertEqual(self.sale_line_2.price_unit, 200)
        self.assertEqual(self.sale_line_2.discount, 0)
        self.assertEqual(self.sale_line_3.price_unit, 300)
        self.assertEqual(self.sale_line_3.discount, 0)
