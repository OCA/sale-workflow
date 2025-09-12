# Copyright 2025 Studio73 - Eugenio Micó <eugenio@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.base.tests.common import BaseCommon


class TestAccountTaxGlobalDiscount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente Test"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Producto Test",
                "list_price": 100,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.discount = cls.env["global.discount"].create(
            {
                "name": "Descuento 10%",
                "discount": 10,
            }
        )
        cls.order.global_discount_ids = [(6, 0, [cls.discount.id])]
        cls.order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product.id,
                "product_uom_qty": 1,
                "price_unit": 100,
            }
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "IVA 21%",
                "amount": 21,
                "type_tax_use": "sale",
            }
        )

    def test_prepare_base_line_for_taxes_computation_with_global_discount(self):
        ctx = dict(self.env.context, from_tax_calculation=True)
        with self.env.cr.savepoint():
            tax = self.tax.with_context(**ctx).sudo()
            kwargs = {"price_unit": 100}
            res = tax._prepare_base_line_for_taxes_computation(
                self.order_line, **kwargs
            )
            discounted = self.order.get_discounted_global(100, [self.discount.discount])
            self.assertEqual(res["price_unit"], discounted)
