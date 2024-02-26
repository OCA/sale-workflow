from odoo.tests.common import SavepointCase


class TestProductSupplierinfoForCustomerSaleBlanketOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls._create_customer("customer_1")
        cls.product = cls.env.ref("product.product_product_4")
        cls.product_variant_1 = cls.env.ref("product.product_product_4b")
        cls.product_variant_2 = cls.env.ref("product.product_product_4c")
        cls.customerinfo = cls._create_partnerinfo(
            "customer", cls.customer, cls.product
        )
        cls.pricelist = cls._create_pricelist("Test Pricelist")
        cls.pricelist_item = cls._create_pricelist_item(
            "Test Pricelist Item", cls.pricelist, cls.product
        )

        cls._create_partnerinfo("customer", cls.customer, cls.product_variant_1)
        cls._create_partnerinfo(
            "customer", cls.customer, cls.product_variant_2, empty_variant=True
        )

    @classmethod
    def _create_customer(cls, name):
        return cls.env["res.partner"].create({"name": name})

    @classmethod
    def _create_partnerinfo(
        cls, supplierinfo_type, partner, product, empty_variant=False
    ):
        vals = {
            "name": partner.id,
            "product_id": product.id,
            "product_name": "test_name",
            "product_code": "test_code",
            "price": 100.0,
            "min_qty": 15.0,
        }
        if empty_variant:
            vals.pop("product_id", None)
            vals["product_tmpl_id"] = product.product_tmpl_id.id
        return cls.env["product." + supplierinfo_type + "info"].create(vals)

    @classmethod
    def _create_pricelist(cls, name):
        return cls.env["product.pricelist"].create(
            {"name": name, "currency_id": cls.env.ref("base.USD").id}
        )

    @classmethod
    def _create_pricelist_item(cls, name, pricelist, product):
        return cls.env["product.pricelist.item"].create(
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
        so = self.env["sale.blanket.order"].create(
            {"partner_id": self.customer.id, "pricelist_id": self.pricelist.id}
        )
        line = self.env["sale.blanket.order.line"].create(
            {
                "product_id": self.product.id,
                "order_id": so.id,
                "product_uom": self.product.uom_id.id,
                "price_unit": 1,
            }
        )
        line.onchange_product()
        self.assertEqual(
            line.product_customer_reference,
            "[%s] %s"
            % (self.customerinfo.product_code, self.customerinfo.product_name),
            "Error: Customer product code was not passed to sale blanket order line",
        )
        self.assertEqual(
            line.original_uom_qty,
            self.customerinfo.min_qty,
            "Error: Min qty was not passed to the sale blanket order line",
        )

    def test_product_supplierinfo_for_customer_sale_variant(self):
        so = self.env["sale.blanket.order"].create(
            {"partner_id": self.customer.id, "pricelist_id": self.pricelist.id}
        )
        line = self.env["sale.blanket.order.line"].create(
            {
                "product_id": self.product_variant_1.id,
                "order_id": so.id,
                "product_uom": self.product_variant_1.uom_id.id,
                "price_unit": 1,
            }
        )
        line.onchange_product()
        self.assertEqual(
            line.product_customer_reference,
            "[%s] %s"
            % (self.customerinfo.product_code, self.customerinfo.product_name),
            "Error: Customer product code was not passed to sale blanket order line",
        )
