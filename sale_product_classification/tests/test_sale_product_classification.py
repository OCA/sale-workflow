# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .test_sale_product_classification_common import (
    TestSaleProductClassificationCase
)
from odoo.fields import Date


class TestSaleProductClassification(TestSaleProductClassificationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_sale_order_classification(self):
        """Generate classifications for diferent period slices"""
        # This is the table of expected classifications according to the
        # generated sales depending on the evaluated period:
        # +------------+------+---+------+---+------+---+------+---+------+---+
        # | From date  |  p1  | C |  p2  | C |  p3  | C |  p4  | c |  p5  | C |
        # +------------+------+---+------+---+------+---+------+---+------+---+
        # | 2021-01-01 | 4000 | C | 2000 | D | 6000 | B | 8000 | B | 5000 | B |
        # | 2021-02-01 | 3000 | C |    0 | D | 6000 | B | 8000 | B |    0 | D |
        # | 2021-03-01 | 2000 | D |    0 | D | 3000 | C | 4000 | C |    0 | D |
        # | 2021-04-01 | 1000 | D |    0 | D | 3000 | C | 4000 | C |    0 | D |
        # +------------+------+---+------+---+------+---+------+---+------+---+
        company = self.env.user.company_id
        cron_classify = self.env["product.product"].cron_sales_classification
        # We want to ensure today's date to simplify the test
        self.mock_date.today.return_value = Date.from_string("2021-04-01")
        # We forced the products create date to 2021-03-01, so they won't be
        # evaluated by the cron if set the days to ignore to 365
        company.sale_classification_days_to_ignore = 365
        cron_classify()
        self.assertFalse(any(self.products.mapped("sale_classification")))
        # Let's reset and now evaluate the a year from now to get all the sales
        # which is the default for sale_classification_days_to_evaluate
        company.sale_classification_days_to_ignore = 0
        cron_classify()
        product_classification = {
            self.prod_1: "c",
            self.prod_2: "d",
            self.prod_3: "b",
            self.prod_4: "b",
            self.prod_5: "b",
        }
        self._test_product_classification(product_classification)
        # 70 from now to get sales from february
        company.sale_classification_days_to_evaluate = 70
        cron_classify()
        product_classification.update({self.prod_5: "d"})
        self._test_product_classification(product_classification)
        # 40 from now to get sales from march
        company.sale_classification_days_to_evaluate = 40
        cron_classify()
        product_classification.update({
            self.prod_1: "d",
            self.prod_4: "c",
            self.prod_3: "c",
        })
        self._test_product_classification(product_classification)
        # Product 1 gets an A!
        self._create_sale("2021-04-01", self.partner, self.prod_1, 20000)
        cron_classify()
        product_classification.update({self.prod_1: "a"})
        self._test_product_classification(product_classification)
