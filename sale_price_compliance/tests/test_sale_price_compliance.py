# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestPriceCompliance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "SPC Partner"})
        # Enable groups Pricelist and discount groups
        cls.env.user.groups_id += cls.env.ref("product.group_product_pricelist")
        cls.env.user.groups_id += cls.env.ref("product.group_discount_per_so_line")
        # Company
        cls.env.company.write(
            {
                "use_price_compliance_threshold": True,
                "price_compliance_threshold_t1": 0.05,
                "price_compliance_threshold_t2": 0.10,
                "price_compliance_threshold_t3": 0.15,
            }
        )
        # Category
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "SPC Category",
                "use_price_compliance_threshold": True,
                "price_compliance_threshold_t1": 0.20,
                "price_compliance_threshold_t2": 0.25,
                "price_compliance_threshold_t3": 0.30,
            }
        )
        # Product: Product with thresholds directly
        cls.product_pct = cls.env["product.product"].create(
            {
                "name": "PCT Product",
                "detailed_type": "service",
                "list_price": 10.0,
                "use_price_compliance_threshold": True,
                "price_compliance_threshold_t1": 0.35,
                "price_compliance_threshold_t2": 0.40,
                "price_compliance_threshold_t3": 0.45,
            }
        )
        # Product: Product with company thresholds
        cls.product_company_pct = cls.env["product.product"].create(
            {
                "name": "PCT Company Product",
                "detailed_type": "service",
                "list_price": 10.0,
            }
        )
        # Product: Product with category thresholds
        cls.product_categ_pct = cls.env["product.product"].create(
            {
                "name": "PCT Categ Product",
                "detailed_type": "service",
                "list_price": 10.0,
                "categ_id": cls.product_category.id,
            }
        )
        # Product: Product with category thresholds and pricelist
        cls.product_pricelist_pct = cls.env["product.product"].create(
            {
                "name": "PCT Pricelist Product",
                "detailed_type": "service",
                "list_price": 10.0,
                "categ_id": cls.product_category.id,
            }
        )
        # Pricelist
        cls.pricelist = (
            cls.env["product.pricelist"]
            .with_company(cls.env.company)
            .create(
                {
                    "name": "PCT Pricelist",
                    "currency_id": cls.env.company.currency_id.id,
                    "item_ids": [
                        Command.create(
                            {
                                "compute_price": "percentage",
                                "percent_price": 50.0,
                                "applied_on": "0_product_variant",
                                "product_id": cls.product_pricelist_pct.id,
                            }
                        )
                    ],
                }
            )
        )

    def _create_sale_order_line(self, product, pricelist=False):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        if pricelist:
            sale.write({"pricelist_id": pricelist.id})
            sale._recompute_prices()
        return sale.order_line[0]

    def _test_price_compliance_discount_tiers(self, sale_line, **tier_data):
        """Test tiers all at once.

        Tier data example:
        {
            "t1": (0.0, 5.0),
            "t2": (5.1, 10.0),
            "t3": (10.1, 15.0),
            "non_compliant": (15.1,),
            "pricelist": (0.0,),
        }

        :param sale_line: Sale Order Line record
        :param tier_data: Data containing tiers to match and discounts.
        """
        for tier_name, tier_values in tier_data.items():
            for tier_val in tier_values:
                with self.subTest(tier=tier_name, discount=tier_val):
                    sale_line.write({"discount": tier_val})
                    self.assertEqual(sale_line.price_compliance_tier, tier_name)

    def test_product_threshold(self):
        """Test product thresholds"""
        self._test_price_compliance_discount_tiers(
            self._create_sale_order_line(self.product_pct),
            t1=(0.0, 35.0),
            t2=(35.1, 40.0),
            t3=(40.1, 45.0),
            non_compliant=(45.1,),
        )

    def test_product_company_threshold(self):
        """Test product company thresholds"""
        self._test_price_compliance_discount_tiers(
            self._create_sale_order_line(self.product_company_pct),
            t1=(0.0, 5.0),
            t2=(5.1, 10.0),
            t3=(10.1, 15.0),
            non_compliant=(15.1,),
        )

    def test_product_category_threshold(self):
        """Test product category thresholds"""
        self._test_price_compliance_discount_tiers(
            self._create_sale_order_line(self.product_categ_pct),
            t1=(0.0, 20.0),
            t2=(20.1, 25.0),
            t3=(25.1, 30.0),
            non_compliant=(30.1,),
        )

    def test_product_pricelist_threshold(self):
        """Test product pricelist thresholds"""
        # Because pricelist applies 50% discount directly inside the price,
        # any discount should go out of Tier ranges and be Non Compliant
        self._test_price_compliance_discount_tiers(
            self._create_sale_order_line(
                self.product_pricelist_pct, pricelist=self.pricelist
            ),
            pricelist=(0.0,),  # Initial price
            non_compliant=(1.0,),  # Any extra discount
        )
