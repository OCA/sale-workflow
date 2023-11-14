from odoo.tests.common import TransactionCase


class TestProductSupplierinfoForCustomerSaleQuick(TransactionCase):
    def setUp(self):
        super(TestProductSupplierinfoForCustomerSaleQuick, self).setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.product_template = self.env["product.template"].create(
            {"name": "Test Product"}
        )
        self.product_customerinfo = self.env["product.customerinfo"].create(
            {
                "name": self.partner.id,
                "product_name": "Test Product",
                "product_code": "123",
                "product_tmpl_id": self.product_template.id,
            }
        )

    def test_search_customer_supplierinfo_data(self):
        """
        Test search_customer_supplierinfo_data method
        by searching for product name and product code.
        """
        self.env.context = {"partner_id": self.partner.id}
        products = self.env["product.product"]

        result_prod_name = products._search_customer_supplierinfo_data(
            "=", "Test Product"
        )
        result_prod_code = products._search_customer_supplierinfo_data("=", "123")
        self.assertEqual(
            result_prod_name,
            [("id", "in", [self.product_template.product_variant_ids.id])],
        )
        self.assertEqual(
            result_prod_code,
            [("id", "in", [self.product_template.product_variant_ids.id])],
        )

        result_wrong_name = products._search_customer_supplierinfo_data(
            "=", "Wrong Product"
        )
        result_wrong_code = products._search_customer_supplierinfo_data("=", "456")
        self.assertEqual(result_wrong_name, [("id", "in", [])])
        self.assertEqual(result_wrong_code, [("id", "in", [])])

        self.env.context = {"partner_id": ""}
        result_empty_name = products._search_customer_supplierinfo_data(
            "=", "Test Product"
        )
        result_empty_code = products._search_customer_supplierinfo_data("=", "123")
        self.assertEqual(result_empty_name, [("id", "in", [])])
        self.assertEqual(result_empty_code, [("id", "in", [])])

    def test_compute_product_customer_info(self):
        """
        Test compute_product_customer_info method
        by computing product_customer_code and product_customer_name.
        """
        self.env.context = {"partner_id": self.partner.id}
        product = self.product_template.product_variant_ids
        product._compute_product_customer_info()

        self.assertEqual(product.product_customer_code, "123")
        self.assertEqual(product.product_customer_name, "Test Product")

        self.env.context = {"partner_id": ""}
        product._compute_product_customer_info()

        self.assertEqual(product.product_customer_code, "")
        self.assertEqual(product.product_customer_name, "")
