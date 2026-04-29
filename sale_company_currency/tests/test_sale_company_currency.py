from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.company = cls.env.ref("base.main_company")
        cls.product1 = cls.env.ref("product.product_product_4")
        cls.product2 = cls.env.ref("product.product_product_5")

        # Fix broken setUpClass: original had two order line dicts
        # inside a single (0, 0, ...) command tuple.
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "company_id": cls.company.id,
                "currency_id": cls.currency_usd.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "product_uom_qty": 2,
                            "price_unit": 50.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )

    def _set_currency_rate(self, currency, rate):
        today = self.sale_order.date_order.date()
        rate_rec = self.env["res.currency.rate"].search(
            [
                ("currency_id", "=", currency.id),
                ("name", "=", today),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )
        if rate_rec:
            rate_rec.rate = rate
        else:
            self.env["res.currency.rate"].create(
                {
                    "currency_id": currency.id,
                    "name": today,
                    "company_id": self.company.id,
                    "rate": rate,
                }
            )

    def test_01_amount_total_curr_same_currency(self):
        self.sale_order.currency_id = self.company.currency_id
        # Force a recompute of amount_total_curr (no manual call)
        self.assertEqual(
            self.sale_order.amount_total_curr,
            self.sale_order.amount_total,
        )

    def test_02_amount_total_curr_different_currency(self):
        self.sale_order.currency_id = self.currency_eur
        # Create rate via res.currency.rate so compute chain is exercised
        self._set_currency_rate(self.currency_eur, 0.85)
        # Flush to trigger recomputes
        self.sale_order.flush_recordset(["amount_total_curr"])
        expected = self.sale_order.amount_total / self.sale_order.currency_rate
        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected,
            places=2,
            msg="Amount in company currency should be converted using division.",
        )

    def test_03_amount_total_curr_rate_one(self):
        self.sale_order.currency_id = self.currency_eur
        self._set_currency_rate(self.currency_eur, 1.0)
        self.sale_order.flush_recordset(["amount_total_curr"])
        self.assertEqual(
            self.sale_order.amount_total_curr,
            self.sale_order.amount_total,
        )

    def test_04_amount_total_curr_multiple_orders(self):
        sale_order_2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "currency_id": self.currency_eur.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_qty": 3,
                            "price_unit": 75.0,
                        },
                    ),
                ],
            }
        )
        self.sale_order.currency_id = self.currency_eur
        self._set_currency_rate(self.currency_eur, 0.85)

        # Flush all modified orders to trigger recomputes
        orders = self.sale_order + sale_order_2
        orders.flush_recordset(["amount_total_curr"])

        expected_1 = self.sale_order.amount_total / self.sale_order.currency_rate
        expected_2 = sale_order_2.amount_total / sale_order_2.currency_rate

        self.assertAlmostEqual(
            self.sale_order.amount_total_curr,
            expected_1,
            places=2,
        )
        self.assertAlmostEqual(
            sale_order_2.amount_total_curr,
            expected_2,
            places=2,
        )

    def test_05_automatic_recompute_on_rate_change(self):
        """Test rate change triggers recomputation of amount_total_curr."""
        self.sale_order.currency_id = self.currency_eur
        self._set_currency_rate(self.currency_eur, 0.5)
        self.sale_order.flush_recordset(["amount_total_curr"])
        first_total_curr = self.sale_order.amount_total_curr

        # Change the rate and check if amount_total_curr is updated automatically
        self._set_currency_rate(self.currency_eur, 0.25)
        self.sale_order.flush_recordset(["amount_total_curr"])

        self.assertNotEqual(self.sale_order.amount_total_curr, first_total_curr)
        expected = self.sale_order.amount_total / 0.25
        self.assertAlmostEqual(self.sale_order.amount_total_curr, expected, places=2)
