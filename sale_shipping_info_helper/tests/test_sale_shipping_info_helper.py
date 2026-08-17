# Copyright 2017 Akretion (Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command
from odoo.tests import Form
from odoo.tools import float_compare

from odoo.addons.base.tests.common import BaseCommon


class TestDeliveryCost(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_model = cls.env["account.tax"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test PL"})
        cls.product_4 = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu"}
        )
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.normal_delivery = cls.env["delivery.carrier"].create(
            {
                "name": "Normal Delivery Charges",
                "fixed_price": 10.0,
                "delivery_type": "fixed",
                "product_id": cls.env["product.product"]
                .create({"name": "Delivery Product", "type": "service"})
                .id,
            }
        )

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
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "name": "PC Assamble + 2GB RAM",
                            "product_id": self.product_4.id,
                            "product_uom_qty": 1,
                            "product_uom_id": self.product_uom_unit.id,
                            "price_unit": 750.00,
                            "tax_ids": [Command.link(self.percent_tax.id)],
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
