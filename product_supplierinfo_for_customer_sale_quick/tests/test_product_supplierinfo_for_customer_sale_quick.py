from odoo.tests.common import TransactionCase


class TestProductSupplierinfoForCustomerSaleQuick(TransactionCase):
    def setUp(self):
        super(TestProductSupplierinfoForCustomerSaleQuick, self).setUp()
        product_attribute = self.env["product.attribute"].create(
            {"name": "PA1", "create_variant": "always", "sequence": 1},
        )

        self.env["product.attribute.value"].create(
            [
                {
                    "name": "PAV" + str(product_attribute.sequence) + str(i),
                    "attribute_id": product_attribute.id,
                }
                for i in range(2)
            ]
        )

        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.product_template = self.env["product.template"].create(
            {
                "name": "Test Product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                    for attribute in product_attribute
                ],
            }
        )

        (
            self.product_var_1,
            self.product_var_2,
        ) = self.product_template.product_variant_ids

        self.product_customerinfo_1 = self.env["product.customerinfo"].create(
            {
                "name": self.partner.id,
                "product_name": "Test Product 1",
                "product_code": "p1 code",
                "product_tmpl_id": self.product_template.id,
                "product_id": self.product_var_1.id,
            }
        )
        self.product_customerinfo_2 = self.env["product.customerinfo"].create(
            {
                "name": self.partner.id,
                "product_name": "Test Product 2",
                "product_code": "p2 code",
                "product_tmpl_id": self.product_template.id,
                "product_id": self.product_var_2.id,
            }
        )

    def test_search_customer_supplierinfo_data(self):
        """
        Test search_customer_supplierinfo_data method
        by searching for product name and product code.
        """
        products = self.env["product.product"].with_context(partner_id=self.partner.id)

        result_prod_p1 = products._search_customer_supplierinfo_data("ilike", "p1")

        self.assertEqual(
            result_prod_p1,
            [("id", "in", [self.product_var_1.id])],
        )

        result_prod_p2 = products._search_customer_supplierinfo_data("ilike", "p2")

        self.assertEqual(
            result_prod_p2,
            [("id", "in", [self.product_var_2.id])],
        )

        result_prod_code = products._search_customer_supplierinfo_data("ilike", "code")

        self.assertEqual(
            result_prod_code,
            [
                ("id", "in", [self.product_var_1.id, self.product_var_2.id]),
            ],
        )
