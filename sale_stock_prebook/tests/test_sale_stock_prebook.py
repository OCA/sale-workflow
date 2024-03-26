from odoo.tests import Form, common, tagged


@tagged("post_install", "-at_install")
class TestStockReserveSale(common.SavepointCase):
    def setUp(self):
        super().setUp()
        partner_form = Form(self.env["res.partner"])
        partner_form.name = "Test partner"
        self.partner = partner_form.save()

        no_prebook_stock_route_id = (
            self.env["stock.location.route"]
            .sudo()
            .create(
                {
                    "name": "Test Route Without Prebook Stock",
                    "no_sale_stock_prebook": True,
                }
            )
        )
        # prebook product
        product_form = Form(self.env["product.product"])
        product_form.name = "Test Product 1"
        product_form.type = "product"
        self.product_1 = product_form.save()
        # non-prebook product
        product_form = Form(self.env["product.product"])
        product_form.name = "Test Product 22"
        product_form.type = "product"
        product_form.route_ids.add(no_prebook_stock_route_id)
        self.product_2 = product_form.save()

        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 3
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_2
            order_line_form.product_uom_qty = 3
        self.sale = sale_order_form.save()

        sale_order_form2 = Form(self.env["sale.order"])
        sale_order_form2.partner_id = self.partner
        with sale_order_form2.order_line.new() as order_line_form2:
            order_line_form2.product_id = self.product_2
            order_line_form2.product_uom_qty = 3
        self.sale2 = sale_order_form2.save()

    def test_10_reserve_and_release(self):
        self.sale.reserve_stock()
        self.sale2.reserve_stock()
        self.assertTrue(self.sale.stock_is_reserved)
        self.assertFalse(self.sale2.stock_is_reserved)
        reservation_pickings = self.sale._get_reservation_pickings()
        self.assertEqual(
            len(reservation_pickings),
            1,
            "There should be one reservation picking created",
        )
        self.assertEqual(
            len(self.sale.picking_ids), 1, "There should be only one picking created"
        )
        self.assertEqual(self.sale.picking_ids.move_lines.product_id, self.product_1)
        self.assertFalse(self.sale2.picking_ids)
        self.sale.release_reservation()
        reservation_pickings = self.sale._get_reservation_pickings()
        self.assertFalse(self.sale.stock_is_reserved)
        self.assertEqual(
            len(reservation_pickings), 0, "There should be no reservation picking"
        )
        self.assertEqual(len(self.sale.picking_ids), 0, "There should be no picking")

    def test_20_confirmation_release(self):
        self.sale.reserve_stock()
        self.sale.action_confirm()
        self.assertFalse(self.sale.stock_is_reserved)

    def test_30_cancelation_release(self):
        self.sale.reserve_stock()
        self.sale.action_cancel()
        self.assertFalse(self.sale.stock_is_reserved)
