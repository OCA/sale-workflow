# Copyright 2017 Akretion (Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import Form, common
from odoo.tools import float_compare


class TestDeliveryCost(common.TransactionCase):
    def setUp(self):
        super(TestDeliveryCost, self).setUp()
        self.tax_model = self.env["account.tax"]
        self.SaleOrder = self.env["sale.order"]
        self.SaleOrderLine = self.env["sale.order.line"]

        self.partner_18 = self.env.ref("base.res_partner_18")
        self.pricelist = self.env.ref("product.list0")
        self.product_4 = self.env.ref("product.product_product_4")
        self.product_uom_unit = self.env.ref("uom.product_uom_unit")
        self.normal_delivery = self.env.ref("delivery.delivery_local_delivery")

    def test_00_shipping_info(self):
        # Create sale order with Normal Delivery Charges
        self.percent_tax = self.tax_model.create(
            {
                "name": "Percent tax",
                "amount_type": "percent",
                "amount": 10,
                "sequence": 3,
            }
        )
        self.normal_delivery.product_id.taxes_id = self.percent_tax
        self.normal_delivery.free_over = False
        self.normal_delivery.amount = 0.0
        self.normal_delivery.fixed_price = 10.0
        self.sale = self.SaleOrder.create(
            {
                "partner_id": self.partner_18.id,
                "partner_invoice_id": self.partner_18.id,
                "partner_shipping_id": self.partner_18.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PC Assamble + 2GB RAM",
                            "product_id": self.product_4.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_uom_unit.id,
                            "price_unit": 750.00,
                            "tax_id": [(4, self.percent_tax.id, 0)],
                        },
                    )
                ],
                "carrier_id": self.normal_delivery.id,
            }
        )

        # set delivery cost in Sales order
        delivery_wizard = Form(
            self.env["choose.delivery.carrier"].with_context(
                default_order_id=self.sale.id,
                default_carrier_id=self.normal_delivery.id,
            )
        )
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        # check sale order computed field after added delivery cost
        line = self.SaleOrderLine.search(
            [
                ("order_id", "=", self.sale.id),
                ("product_id", "=", self.sale.carrier_id.product_id.id),
            ]
        )
        self.assertEqual(len(line), 1, "Delivery cost is not Added")
        self.assertEqual(
            float_compare(line.price_subtotal, 10, precision_digits=2),
            0,
            "Sale line delivery price subtotal is not correct",
        )
        self.assertEqual(
            float_compare(line.price_total, 11, precision_digits=2),
            0,
            "Sale line delivery price total is not correct",
        )
        self.assertEqual(
            float_compare(line.price_tax, 1, precision_digits=2),
            0,
            "Sale line delivery price tax is not correct",
        )
        self.assertEqual(
            float_compare(self.sale.shipping_amount_tax, 1, precision_digits=2),
            0,
            "Shipping amount tax is not correct",
        )
        self.assertEqual(
            float_compare(self.sale.shipping_amount_untaxed, 10, precision_digits=2),
            0,
            "Shipping amount untaxed is not correct",
        )
        self.assertEqual(
            float_compare(self.sale.shipping_amount_total, 11, precision_digits=2),
            0,
            "Shipping amount total is not correct",
        )
        self.assertEqual(
            float_compare(self.sale.item_amount_tax, 75, precision_digits=2),
            0,
            "Item amount tax is not correct",
        )
        self.assertEqual(
            float_compare(self.sale.item_amount_untaxed, 750, precision_digits=2),
            0,
            "Item amount untaxed is not correct",
        )
        self.assertEqual(
            float_compare(self.sale.item_amount_total, 825.0, precision_digits=2),
            0,
            "Item amount total is not correct",
        )
