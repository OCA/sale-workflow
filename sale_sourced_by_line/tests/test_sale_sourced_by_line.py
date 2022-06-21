# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 ForgeFlow S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestSaleSourcedByLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleSourcedByLine, cls).setUpClass()
        cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.company_shop = cls.env.ref("stock.res_company_1")

        # Create user for company Chicago
        cls.user = cls.env["res.users"].create(
            {
                "login": "Salesman Chicago Sourced By Line",
                "email": "test@test.com",
                "name": "Salesman Chicago Sourced By Line",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
                "company_ids": [(6, 0, (cls.company | cls.company_shop).ids)],
                "company_id": cls.company_shop.id,
            }
        )

        cls.sale_order_model = cls.env["sale.order"].with_user(cls.user)
        cls.sale_order_line_model = cls.env["sale.order.line"].with_user(cls.user)
        cls.stock_move_model = cls.env["stock.move"]

        # Refs
        cls.customer = cls.env.ref("base.res_partner_2")
        cls.product_1 = cls.env.ref("product.product_product_27")
        cls.product_2 = cls.env.ref("product.product_product_24")
        cls.warehouse_shop0 = cls.env.ref("stock.stock_warehouse_shop0")
        cls.warehouse0 = cls.env.ref("stock.warehouse0")

    def test_sales_order_multi_source(self):
        so = self.sale_order_model.create({"partner_id": self.customer.id})
        self.sale_order_line_model.create(
            {
                "product_id": self.product_1.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse_shop0.id,
                "order_id": so.id,
            }
        )
        self.sale_order_line_model.create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse0.id,
                "order_id": so.id,
            }
        )
        # confirm quotation
        so.action_confirm()
        self.assertEquals(
            len(so.picking_ids),
            2,
            "2 delivery orders expected. Got %s instead" % len(so.picking_ids),
        )
        for line in so.order_line:
            self.assertEquals(
                line.procurement_group_id.name,
                line.order_id.name + "/" + line.warehouse_id.name,
                "The name of the procurement group is not " "correct.",
            )
            for move in line.move_ids:
                self.assertEquals(
                    move.group_id,
                    line.procurement_group_id,
                    "The group in the stock move does not "
                    "match with the procurement group in "
                    "the sales order line.",
                )
                self.assertEquals(
                    move.picking_id.group_id,
                    line.procurement_group_id,
                    "The group in the stock picking does "
                    "not match with the procurement group "
                    "in the sales order line.",
                )

    def test_sales_order_no_source(self):
        so = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "warehouse_id": self.warehouse_shop0.id,
                "company_id": self.warehouse_shop0.company_id.id,
            }
        )
        self.sale_order_line_model.create(
            {"product_id": self.product_1.id, "product_uom_qty": 8, "order_id": so.id}
        )
        self.sale_order_line_model.create(
            {"product_id": self.product_2.id, "product_uom_qty": 8, "order_id": so.id}
        )
        # confirm quotation
        so.action_confirm()
        self.assertEquals(
            len(so.picking_ids),
            1,
            "1 delivery order expected. Got %s instead" % len(so.picking_ids),
        )

    def test_sale_order_source(self):
        so = self.sale_order_model.create({"partner_id": self.customer.id})
        self.sale_order_line_model.create(
            {
                "product_id": self.product_1.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse_shop0.id,
                "order_id": so.id,
            }
        )
        self.sale_order_line_model.create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse0.id,
                "order_id": so.id,
            }
        )
        # confirm quotation
        so.action_confirm()
        for line in so.order_line:
            for stock_move in line.move_ids:
                self.assertEquals(
                    stock_move.warehouse_id,
                    line.warehouse_id,
                    "The warehouse in the stock.move does not "
                    "match with the Sales order line.",
                )
