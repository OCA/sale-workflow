# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderActionCreateHook(TransactionCase):
    def setUp(self):
        super(TestSaleOrderActionCreateHook, self).setUp()
        self.users_obj = self.env["res.users"]
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]

        # company
        self.company1 = self.env.ref("base.main_company")

        # customer
        self.customer = self._create_customer("Test Customer")

        # product
        product_ctg = self._create_product_category()
        self.service_1 = self._create_product("test_product1", product_ctg)
        self.service_2 = self._create_product("test_product2", product_ctg)

    def _create_customer(self, name):
        """Create a Partner."""
        return self.env["res.partner"].create(
            {
                "name": name,
                "email": "example@yourcompany.com",
                "customer": True,
                "phone": 123456,
                "currency_id": self.env.ref("base.EUR"),
            }
        )

    def _create_product_category(self):
        product_ctg = self.env["product.category"].create({"name": "test_product_ctg",})
        return product_ctg

    def _create_product(self, name, product_ctg):
        product = self.env["product.product"].create(
            {"name": name, "categ_id": product_ctg.id, "type": "service",}
        )
        return product

    def values_sale_order(self):
        return {
            "partner_id": self.customer.id,
        }

    def _create_sale_order(self):
        so = self.sale_order_model.create({"partner_id": self.customer.id,})
        sol1 = self.sale_order_line_model.create(
            {"product_id": self.service_1.id, "product_uom_qty": 1, "order_id": so.id,}
        )
        sol2 = self.sale_order_line_model.create(
            {"product_id": self.service_2.id, "product_uom_qty": 2, "order_id": so.id,}
        )
        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 1
        sol2.qty_delivered = 2
        return so

    def _create_invoice_from_sale(self, sale):
        data = {"advance_payment_method": "delivered"}
        payment = self.env["sale.advance.payment.inv"].create(data)
        sale_context = {
            "active_id": sale.id,
            "active_ids": sale.ids,
            "active_model": "sale.order",
            "open_invoices": True,
        }
        res = payment.with_context(sale_context).create_invoices()
        invoice_id = self.env["account.move"].browse(res["res_id"])
        return invoice_id

    def test_create_invoice_case_1(self):
        so1 = self._create_sale_order()
        inv1 = self._create_invoice_from_sale(so1)
        self.assertNotEquals(inv1, False)
