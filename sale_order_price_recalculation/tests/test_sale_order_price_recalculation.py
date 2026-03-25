# Copyright 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2018 Duc Dao Dong <duc.dd@komit-consulting.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderPriceRecalculation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable group_discount_per_so_line for admin user
        group = cls.env.ref("sale.group_discount_per_so_line")
        group.user_ids = [Command.link(cls.env.user.id)]
        uom_id = cls.env.ref("uom.product_uom_kgm")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Jacket - Color: Black - Size: XL",
                "uom_id": uom_id.id,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    ),
                ],
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
            }
        )
        line_vals = {
            "product_id": cls.product.id,
            "product_template_id": cls.product.product_tmpl_id.id,
            "name": cls.product.name,
            "product_uom_qty": 1.0,
            "product_uom_id": cls.product.uom_id.id,
            "price_unit": cls.product.lst_price,
            "order_id": cls.sale_order.id,
        }
        cls.sale_order_line = cls.env["sale.order.line"].create(line_vals)

    def test_name_recalculation(self):
        self.sale_order_line.price_unit = 150.0
        initial_price = self.sale_order_line.price_unit
        self.assertEqual(self.sale_order_line.name, self.product.name)
        self.sale_order_line.name = "Custom Jacket"
        self.sale_order.action_update_names()
        self.assertNotEqual("Custom Jacket", self.sale_order_line.name)
        # Check the price wasn't reset
        self.assertEqual(initial_price, self.sale_order_line.price_unit)
