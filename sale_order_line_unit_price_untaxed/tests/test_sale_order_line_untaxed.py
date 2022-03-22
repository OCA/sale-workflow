# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.fields import first
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestSalePriceUntaxed(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )
        cls.tmpl_obj = cls.env["product.template"]
        cls.prod_obj = cls.env["product.product"]
        cls.company_obj = cls.env["res.company"]
        cls.company = cls.env.ref("base.main_company")
        vals = {
            "name": "Company 2",
        }
        cls.company_2 = cls.company_obj.create(vals)

        # Tax excluded from price in main company
        cls.tax1 = cls.env["account.tax"].create(
            {
                "name": "Test Tax Excluded",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 15,
                "price_include": False,
                "company_id": cls.company.id,
            }
        )
        # Tax included from price in Company 2
        cls.tax2 = cls.env["account.tax"].create(
            {
                "name": "Test Taxe Included",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 15,
                "price_include": True,
                "company_id": cls.company_2.id,
            }
        )
        cls.tmpl = cls.tmpl_obj.create(
            {
                "name": "NewTmpl",
                "taxes_id": [(4, cls.tax1.id), (4, cls.tax2.id)],
                "list_price": 115.0,
            }
        )
        cls.product = cls.tmpl.product_variant_ids[0]

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.user_demo.write(
            {"groups_id": [(4, cls.env.ref("sales_team.group_sale_manager").id)]}
        )

        cls.user_demo.write(
            {
                "company_id": cls.company.id,
                "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
            }
        )
        cls.precision = cls.env["decimal.precision"].search(
            [("name", "=", "Product Price")]
        )

    def test_sale_with_product_main_company(self):
        user_demo = self.env.ref("base.user_demo")
        user_demo.write(
            {"groups_id": [(4, self.env.ref("sales_team.group_sale_manager").id)]}
        )

        pricelist = self.partner.with_company(self.company).property_product_pricelist
        so = (
            self.env["sale.order"]
            .with_user(user_demo.id)
            .with_company(self.company)
            .create(
                {
                    "partner_id": self.partner.id,
                    "pricelist_id": pricelist.id,
                }
            )
        )
        sol1 = (
            self.env["sale.order.line"]
            .with_user(user_demo.id)
            .with_company(self.company)
            .create({"order_id": so.id, "product_id": self.product.id})
        )
        self.assertEqual(sol1.price_unit, 115)
        self.assertEqual(sol1.price_unit_untaxed, 115)

    def test_sale_with_product_company2(self):
        user_demo = self.env.ref("base.user_demo")
        user_demo.write(
            {
                "groups_id": [(4, self.env.ref("sales_team.group_sale_manager").id)],
                "company_id": self.company_2.id,
            }
        )
        pricelist = self.partner.with_company(self.company_2).property_product_pricelist
        so2 = (
            self.env["sale.order"]
            .with_user(user_demo.id)
            .with_company(self.company_2)
            .create(
                {
                    "partner_id": self.partner.id,
                    "pricelist_id": pricelist.id,
                }
            )
        )
        self.product.refresh()
        self.env["sale.order.line"].invalidate_cache()
        sol2 = (
            self.env["sale.order.line"]
            .with_user(user_demo.id)
            .with_company(self.company_2)
            .create({"order_id": so2.id, "product_id": self.product.id})
        )
        self.assertEqual(sol2.price_unit, 115)
        self.assertEqual(sol2.price_unit_untaxed, 100)

    def test_sale_with_decimal_precision(self):
        """
        Set tax with price include False
        Set the product price to 118.573
        Set product price precision to 3
        Check prices are equivalent (price_unit == price_unit_untaxed) with
        same
        """
        self.tax2.price_include = False
        self.user_demo.write(
            {
                "company_id": self.company_2.id,
            }
        )
        so2 = (
            self.env["sale.order"]
            .with_user(self.user_demo)
            .with_company(self.company_2)
            .create(
                {
                    "partner_id": self.partner.id,
                }
            )
        )
        self.precision.write({"digits": 3})
        self.product.list_price = 118.573
        with Form(so2) as order_form:
            with order_form.order_line.new() as order_line:
                order_line.product_id = self.product
        order_line = first(so2.order_line)
        self.assertEqual(order_line.price_unit, 118.573)
        self.assertAlmostEqual(
            order_line.price_unit_untaxed, 118.573, places=self.precision.digits
        )
