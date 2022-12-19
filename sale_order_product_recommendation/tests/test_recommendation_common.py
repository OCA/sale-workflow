# Copyright 2017 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class RecommendationCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        all_category = cls.env.ref("product.product_category_all")
        cls.product_categ_1 = cls.env["product.category"].create(
            {
                "name": "Category 1",
                "parent_id": all_category.id,
            }
        )
        cls.product_categ_2 = cls.env["product.category"].create(
            {
                "name": "Category 2",
                "parent_id": all_category.id,
            }
        )
        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "Attribute test",
                "display_type": "select",
                "create_variant": "no_variant",
            }
        )
        cls.attribute_value_1 = cls.env["product.attribute.value"].create(
            {"name": "Attribute value 1", "attribute_id": cls.attribute.id}
        )
        cls.attribute_value_2 = cls.env["product.attribute.value"].create(
            {"name": "Attribute value 2", "attribute_id": cls.attribute.id}
        )
        cls.product_obj = cls.env["product.product"]
        cls.prod_1 = cls.product_obj.create(
            {
                "name": "Test Product 1",
                "categ_id": cls.product_categ_1.id,
                "type": "service",
                "list_price": 25.00,
            }
        )
        cls.prod_1.product_tmpl_id.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(4, cls.attribute_value_1.id)],
                        },
                    )
                ],
            }
        )
        cls.prod_2 = cls.product_obj.create(
            {
                "name": "Test Product 2",
                "categ_id": cls.product_categ_2.id,
                "type": "service",
                "list_price": 50.00,
            }
        )
        cls.prod_3 = cls.product_obj.create(
            {
                "name": "Test Product 3",
                "type": "service",
                "list_price": 75.00,
            }
        )
        # Create old sale orders to have searchable history
        cls.order1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "state": "done",
                "date_order": "2020-11-15",
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
                "state": "done",
                "date_order": "2020-11-10",
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
