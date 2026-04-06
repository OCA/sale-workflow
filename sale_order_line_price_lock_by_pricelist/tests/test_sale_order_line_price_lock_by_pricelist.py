# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.tests import Form, common, users

from odoo.addons.mail.tests.common import mail_new_test_user


class TestSaleOrderLinePriceLockByPricelist(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_with_locked_price = cls.env["product.template"].create(
            {
                "name": "Test product 1",
                "list_price": 100.0,
            }
        )
        cls.product_other = cls.env["product.template"].create(
            {
                "name": "Test product 2",
                "list_price": 120.0,
            }
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo",
            }
        )
        cls.pricelist_1 = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist 1",
                "lock_product_prices_applied_on": "1_product",  # Lock scope set to Product
            }
        )
        cls.pricelist_2 = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist 1",
                "lock_product_prices_applied_on": "1_product",  # Lock scope set to Product
            }
        )
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist_1.id,
                "compute_price": "formula",
                "base": "list_price",
                "applied_on": "3_global",
            }
        )
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist_1.id,
                "compute_price": "fixed",
                "applied_on": "1_product",
                "product_tmpl_id": cls.product_with_locked_price.id,
                "fixed_price": 80.0,
            }
        )
        cls.user_sales_salesman = mail_new_test_user(
            cls.env,
            login="user_sales_salesman",
            name="Manolo Sales Own",
            email="crm_salesman@test.example.com",
            company_id=cls.env.company.id,
            notification_type="inbox",
            groups="sales_team.group_sale_salesman",
        )
        cls.user_sales_salesman = mail_new_test_user(
            cls.env,
            login="user_sales_sales_manager",
            name="Paco Sales Manager",
            email="crm_salesmanager@test.example.com",
            company_id=cls.env.company.id,
            notification_type="inbox",
            groups="sales_team.group_sale_manager",
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo",
            }
        )

    def _create_sales_order(self):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.customer
        sale_form.pricelist_id = self.pricelist_1
        with sale_form.order_line.new() as line:
            line.product_id = self.product_other.product_variant_id
            line.price_unit = 5
        return sale_form

    @users("user_sales_salesman")
    def test_price_lock_on_pricelist_salesman(self):
        sale_form = self._create_sales_order()
        with sale_form.order_line.new() as line:
            line.product_id = self.product_with_locked_price.product_variant_id
            # It's readonly, so we can't edit it
            with self.assertRaises(AssertionError):
                line.price_unit = 5

    @users("user_sales_salesman")
    def test_price_lock_on_other_pricelist_salesman(self):
        sale_form = self._create_sales_order()
        sale_form.pricelist_id = self.pricelist_2
        with sale_form.order_line.new() as line:
            line.product_id = self.product_with_locked_price.product_variant_id
            line.price_unit = 5

    @users("user_sales_sales_manager")
    def test_price_lock_on_pricelist_manager(self):
        """Sales manager don't have any constraint on the price lock"""
        sale_form = self._create_sales_order()
        with sale_form.order_line.new() as line:
            line.product_id = self.product_with_locked_price.product_variant_id
            line.price_unit = 5
