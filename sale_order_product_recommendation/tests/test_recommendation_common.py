# Copyright 2017 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class RecommendationCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        # Make sure user has UoM activated for Forms to work
        cls.env.user.groups_id = [(4, cls.env.ref("uom.group_uom").id)]
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist for test",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Mr. Odoo", "property_product_pricelist": cls.pricelist.id}
        )
        cls.partner_delivery = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo Delivery",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product_obj = cls.env["product.product"]
        cls.prod_1 = cls.product_obj.create(
            {
                "name": "Test Product 1",
                "detailed_type": "service",
                "list_price": 25.00,
            }
        )
        cls.prod_2 = cls.product_obj.create(
            {
                "name": "Test Product 2",
                "detailed_type": "service",
                "list_price": 50.00,
            }
        )
        cls.prod_3 = cls.product_obj.create(
            {
                "name": "Test Product 3",
                "detailed_type": "service",
                "list_price": 75.00,
            }
        )
        # Create old sale orders to have searchable history
        # (Remember to change the dates if the tests fail)
        cls.order1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "state": "done",
                "date_order": "2021-05-05",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_1.id,
                            "name": cls.prod_1.name,
                            "product_uom_qty": 25,
                            "qty_delivered_method": "manual",
                            "qty_delivered": 25,
                            "price_unit": 24.50,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_2.id,
                            "name": cls.prod_2.name,
                            "product_uom_qty": 50,
                            "qty_delivered_method": "manual",
                            "qty_delivered": 50,
                            "price_unit": 49.50,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_3.id,
                            "name": cls.prod_3.name,
                            "product_uom_qty": 100,
                            "qty_delivered_method": "manual",
                            "qty_delivered": 100,
                            "price_unit": 74.50,
                        },
                    ),
                ],
            }
        )
        cls.order2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_shipping_id": cls.partner_delivery.id,
                "state": "done",
                "date_order": "2021-05-03",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod_2.id,
                            "name": cls.prod_2.name,
                            "product_uom_qty": 50,
                            "qty_delivered_method": "manual",
                            "qty_delivered": 50,
                            "price_unit": 89.00,
                        },
                    ),
                ],
            }
        )
        # Create a new sale order for the same customer
        cls.new_so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

    def wizard(self):
        """Get a wizard."""
        wizard = (
            self.env["sale.order.recommendation"]
            .with_context(active_id=self.new_so.id)
            .create({})
        )
        wizard._generate_recommendations()
        return wizard

    def enable_force_zero_units_included(self):
        self.settings = self.env["res.config.settings"].create({})
        self.settings.force_zero_units_included = True
        self.settings.set_values()
