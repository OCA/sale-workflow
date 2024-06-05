# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestProductSupplierinfoForCustomerSale(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplierinfo_model = cls.env["product.supplierinfo"]
        cls.customerinfo_model = cls.env["product.customerinfo"]
        cls.pricelist_item_model = cls.env["product.pricelist.item"]
        cls.pricelist_model = cls.env["product.pricelist"]
        cls.customer = cls._create_customer("customer1")
        cls.product = cls.env.ref("product.product_product_4")
        cls.product_variant_1 = cls.env.ref("product.product_product_4b")
        cls.product_variant_2 = cls.env.ref("product.product_product_4c")
        cls.customerinfo = cls._create_partnerinfo(
            "customer", cls.customer, cls.product
        )
        cls.pricelist = cls._create_pricelist("Test Pricelist", cls.product)
        cls.pricelist_item = cls._create_pricelist_item(
            "Test Pricelist Item", cls.pricelist, cls.product
        )
        cls.company = cls.env.ref("base.main_company")
        cls._create_partnerinfo("customer", cls.customer, cls.product_variant_1)
        cls._create_partnerinfo(
            "customer", cls.customer, cls.product_variant_2, empty_variant=True
        )
        cls.product_template = cls.env["product.template"].create(
            {"name": "product wo variants"}
        )
        cls._create_partnerinfo(
            "customer",
            cls.customer,
            cls.product_template.product_variant_ids[:1],
            empty_variant=True,
        )
        cls.pricelist_template = cls._create_pricelist(
            "Test Pricelist Template", cls.product_template.product_variant_ids[:1]
        )
        cls.env.user.groups_id |= cls.env.ref("product.group_product_pricelist")

    @classmethod
    def _create_customer(cls, name):
        return cls.env["res.partner"].create(
            {"name": name, "email": "example@yourcompany.com", "phone": 123456}
        )

    @classmethod
    def _create_partnerinfo(
        cls, supplierinfo_type, partner, product, empty_variant=False
    ):
        vals = {
            "partner_id": partner.id,
            "product_id": product.id,
            "product_name": "product4",
            "product_code": "00001",
            "price": 100.0,
            "min_qty": 15.0,
        }
        if empty_variant:
            vals.pop("product_id", None)
            vals["product_tmpl_id"] = product.product_tmpl_id.id
        return cls.env["product." + supplierinfo_type + "info"].create(vals)

    @classmethod
    def _create_pricelist(cls, name, product):
        return cls.pricelist_model.create(
            {"name": name, "currency_id": cls.env.ref("base.USD").id}
        )

    @classmethod
    def _create_pricelist_item(cls, name, pricelist, product):
        return cls.pricelist_item_model.create(
            {
                "name": name,
                "pricelist_id": pricelist.id,
                "applied_on": "0_product_variant",
                "product_id": product.id,
                "compute_price": "formula",
                "base": "partner",
            }
        )

    def test_product_supplierinfo_for_customer_sale(self):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.customer
        order_form.pricelist_id = self.pricelist
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        order = order_form.save()
        line = order.order_line
        self.assertIn("00001", order.order_line.name)
        self.assertEqual(
            line.product_customer_code,
            self.customerinfo.product_code,
            "Error: Customer product code was not passed to sale order line",
        )
        self.assertEqual(
            line.product_uom_qty,
            self.customerinfo.min_qty,
            "Error: Min qty was not passed to the sale order line",
        )

    def test_product_supplierinfo_for_customer_sale_variant(self):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.customer
        order_form.pricelist_id = self.pricelist
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_variant_1
        order = order_form.save()
        line = order.order_line
        self.assertEqual(
            line.product_customer_code,
            self.customerinfo.product_code,
            "Error: Customer product code was not passed to sale order line",
        )

    def test_product_supplierinfo_for_customer_sale_template(self):
        customerinfo = self._create_partnerinfo(
            "customer", self.customer, self.product_variant_2
        )
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.customer
        order_form.pricelist_id = self.pricelist
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_variant_2
        order = order_form.save()
        line = order.order_line
        self.assertEqual(
            line.product_customer_code,
            customerinfo.product_code,
            "Error: Customer product code was not passed to sale order line",
        )
        # Test with product without variants
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.customer
        order_form.pricelist_id = self.pricelist_template
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_template.product_variant_ids[0]
        order2 = order_form.save()
        line2 = order2.order_line
        self.assertEqual(
            line2.product_customer_code,
            customerinfo.product_code,
            "Error: Customer product code was not passed to sale order line",
        )

    def test_product_supplierinfo_for_customer_sale_variant_wo_template(self):
        customerinfo = self._create_partnerinfo(
            "customer", self.customer, self.product_variant_2, empty_variant=True
        )
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.customer
        order_form.pricelist_id = self.pricelist
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_variant_2
        order = order_form.save()
        line = order.order_line
        self.assertEqual(
            line.product_customer_code,
            customerinfo.product_code,
            "Error: Customer product code was not passed to sale order line",
        )
