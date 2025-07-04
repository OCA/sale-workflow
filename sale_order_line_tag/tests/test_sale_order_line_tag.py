from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLineTag(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100,
            }
        )
        cls.line_tag_model = cls.env["sale.order.line.tag"]
        cls.order_model = cls.env["sale.order"]

        # Test tags
        cls.tag_discount = cls.line_tag_model.create({"name": "Discount"})
        cls.tag_campaign = cls.line_tag_model.create({"name": "Campaign"})
        cls.tag_urgent = cls.line_tag_model.create({"name": "Urgent"})

    def test_assign_single_tag_to_order_line(self):
        """Assign a single tag to a sale order line"""
        sale_form = Form(self.order_model)
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1
            line.tag_ids.add(self.tag_discount)
        sale_order = sale_form.save()

        self.assertEqual(len(sale_order.order_line), 1)
        self.assertIn(self.tag_discount, sale_order.order_line.tag_ids)

    def test_assign_multiple_tags_to_order_line(self):
        """Assign multiple tags to a single sale order line"""
        sale_form = Form(self.order_model)
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 2
            line.tag_ids.add(self.tag_campaign)
            line.tag_ids.add(self.tag_urgent)
        sale_order = sale_form.save()

        tags = sale_order.order_line.tag_ids
        self.assertEqual(tags, self.tag_campaign + self.tag_urgent)

    def test_filter_lines_by_tag(self):
        """Search sale order lines by a specific tag"""
        sale_form = Form(self.order_model)
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1
            line.tag_ids.add(self.tag_urgent)
        sale_order = sale_form.save()

        lines_with_tag = self.env["sale.order.line"].search(
            [("tag_ids", "in", self.tag_urgent.id)]
        )
        self.assertIn(sale_order.order_line, lines_with_tag)
