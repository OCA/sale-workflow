from odoo.tests import TransactionCase


class TestPricelistAncestor(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.env.user.groups_id += cls.env.ref("sale.group_discount_per_so_line")

        # --- UoM & Partner
        cls.uom_unit = env.ref("uom.product_uom_unit")
        cls.partner = env["res.partner"].create({"name": "Test Customer"})

        # --- Category tree:
        # Cat A
        # ├─ Cat B
        # └─ Cat C
        #    └─ Cat D
        cls.cat_a = env["product.category"].create({"name": "Cat A"})
        cls.cat_b = env["product.category"].create(
            {"name": "Cat B", "parent_id": cls.cat_a.id}
        )
        cls.cat_c = env["product.category"].create(
            {"name": "Cat C", "parent_id": cls.cat_a.id}
        )
        cls.cat_d = env["product.category"].create(
            {"name": "Cat D", "parent_id": cls.cat_c.id}
        )

        # --- Products (list_price=100 for easy math)
        def _mk(name, categ):
            tmpl = env["product.template"].create(
                {
                    "name": name,
                    "list_price": 100.0,
                    "uom_id": cls.uom_unit.id,
                    "uom_po_id": cls.uom_unit.id,
                    "categ_id": categ.id,
                    "type": "consu",
                }
            )
            return tmpl.product_variant_id

        cls.prod_a = _mk("Prod A", cls.cat_a)
        cls.prod_b = _mk("Prod B", cls.cat_b)
        cls.prod_c = _mk("Prod C", cls.cat_c)
        cls.prod_d = _mk("Prod D", cls.cat_d)

        # Pricelist helper (show discount column)
        def _mk_pl(name):
            return env["product.pricelist"].create(
                {
                    "name": name,
                    "currency_id": env.ref("base.USD").id,
                }
            )

        def _mk_item(
            pricelist,
            display_applied_on,
            applied_on,
            compute_price,
            percent_price,
            min_quantity,
            name,
            ancestor_product_category=None,
            product=None,
        ):
            vals = {
                "pricelist_id": pricelist.id,
                "display_applied_on": display_applied_on,
                "compute_price": compute_price,
                "percent_price": percent_price,
                "min_quantity": min_quantity,
                "name": name,
            }
            if display_applied_on == "3_global":
                vals.update({"global_applied_on": applied_on})
            else:
                vals.update({"applied_on": applied_on})

            if ancestor_product_category:
                vals["ancestor_product_category_id"] = ancestor_product_category.id
            if product:
                vals["product_id"] = product.id
            return env["product.pricelist.item"].create(vals)

        # --- PRICELIST for Test Case 1
        cls.pl_case1 = _mk_pl("Price List 1")
        # PI0: Variant Prod A -> 30%
        cls.pi0 = _mk_item(
            cls.pl_case1,
            "1_product",
            "1_product",
            "percentage",
            30.0,
            1.0,
            "PI0",
            product=cls.prod_a,
        )
        # PI1: Ancestor Cat C -> 20% (min 5)
        cls.pi1 = _mk_item(
            cls.pl_case1,
            "3_global",
            "3_3_global_product_ancestor_category",
            "percentage",
            20.0,
            5.0,
            "PI1",
            ancestor_product_category=cls.cat_c,
        )
        # PI2: Ancestor Cat A -> 10% (min 5)
        cls.pi2 = _mk_item(
            cls.pl_case1,
            "3_global",
            "3_3_global_product_ancestor_category",
            "percentage",
            10.0,
            5.0,
            "PI2",
            ancestor_product_category=cls.cat_a,
        )

        # --- PRICELIST for Test Case 2
        cls.pl_case2 = _mk_pl("Price List 2")
        # PI0': Ancestor Cat C -> 20%
        cls.pi0p = _mk_item(
            cls.pl_case2,
            "3_global",
            "3_3_global_product_ancestor_category",
            "percentage",
            20.0,
            5.0,
            "PI0'",
            ancestor_product_category=cls.cat_c,
        )
        # PI1': Ancestor Cat A -> 10%
        cls.pi1p = _mk_item(
            cls.pl_case2,
            "3_global",
            "3_3_global_product_ancestor_category",
            "percentage",
            10.0,
            5.0,
            "PI1'",
            ancestor_product_category=cls.cat_a,
        )

    # ---------- tests ----------
    def test_case_1_best_percentage_and_ancestor_totals(self):
        """
        Case 1:
        - Rules: PI0 (Prod A 30%), PI1 (Cat C 20%, min=5), PI2 (Cat A 10%, min=5)
        - Order lines: A(2), B(2), C(4), D(2)
        - Totals: Cat A branch=10, Cat C branch=6
        Expected:
        - A → PI0 (30%)
        - B → PI2 (10%)
        - C → PI1 (20%)
        - D → PI1 (20%)
        """
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pl_case1.id}
        )
        l1 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_a.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 2,
                "name": self.prod_a.name,
                "price_unit": self.prod_a.list_price,
            }
        )
        l2 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_b.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 2,
                "name": self.prod_b.name,
                "price_unit": self.prod_b.list_price,
            }
        )
        l3 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_c.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 4,
                "name": self.prod_c.name,
                "price_unit": self.prod_c.list_price,
            }
        )
        l4 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_d.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 2,
                "name": self.prod_d.name,
                "price_unit": self.prod_d.list_price,
            }
        )

        # recompute using module's action
        order.button_compute_pricelist_global_rule()

        self.assertEqual(l1.pricelist_item_id, self.pi0)
        self.assertEqual(l2.pricelist_item_id, self.pi2)
        self.assertEqual(l3.pricelist_item_id, self.pi1)
        self.assertEqual(l4.pricelist_item_id, self.pi1)

        self.assertAlmostEqual(l1.discount, 30.0)
        self.assertAlmostEqual(l2.discount, 10.0)
        self.assertAlmostEqual(l3.discount, 20.0)
        self.assertAlmostEqual(l4.discount, 20.0)

    def test_case_2_best_percentage(self):
        """
        Case 2:
        - Rules: PI0' (Cat C 20%), PI1' (Cat A 10%)
        - Order lines: A(2), B(2), C(4), D(2)
        Expected:
        - A → PI1' (10%) because Cat A branch total=10
        - B → PI1' (10%)
        - C → PI0' (20%) because Cat C branch total=6
        - D → PI0' (20%)
        """
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "pricelist_id": self.pl_case2.id}
        )
        l1 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_a.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 2,
                "name": self.prod_a.name,
                "price_unit": self.prod_a.list_price,
            }
        )
        l2 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_b.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 2,
                "name": self.prod_b.name,
                "price_unit": self.prod_b.list_price,
            }
        )
        l3 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_c.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 4,
                "name": self.prod_c.name,
                "price_unit": self.prod_c.list_price,
            }
        )
        l4 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.prod_d.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 2,
                "name": self.prod_d.name,
                "price_unit": self.prod_d.list_price,
            }
        )

        order.button_compute_pricelist_global_rule()

        self.assertEqual(l1.pricelist_item_id, self.pi1p)
        self.assertEqual(l2.pricelist_item_id, self.pi1p)
        self.assertEqual(l3.pricelist_item_id, self.pi0p)
        self.assertEqual(l4.pricelist_item_id, self.pi0p)

        self.assertAlmostEqual(l1.discount, 10.0)
        self.assertAlmostEqual(l2.discount, 10.0)
        self.assertAlmostEqual(l3.discount, 20.0)
        self.assertAlmostEqual(l4.discount, 20.0)
