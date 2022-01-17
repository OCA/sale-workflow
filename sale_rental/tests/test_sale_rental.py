
from odoo.tests.common import TransactionCase
from odoo.tests import Form
from odoo.exceptions import UserError


class TestSaleRental(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_rental_prod = cls.env.ref(
            "sale_rental.rent_product_product_25")
        cls.test_partner = cls.env["res.partner"].create({"name": "Foo"})
        cls.rental_in_loc = cls.env.ref("stock.warehouse0").rental_in_location_id
        cls.rental_out_loc = cls.env.ref("stock.warehouse0").rental_out_location_id

    def test_main(self):
        # Rent a product
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.test_partner
        with so_form.order_line.new() as line:
            line.product_id = self.test_rental_prod
            line.start_date = "2022-01-01"
            line.end_date = "2022-01-10"
            line.rental_qty = 1
        so = so_form.save()
        sol = so.order_line
        self.assertEqual(sol.price_subtotal, 60)
        so.action_confirm()
        self.assertEqual(len(so.picking_ids), 2)
        rental_out_pick = so.picking_ids.filtered(
            lambda p:
            p.location_id == self.rental_in_loc
            and p.location_dest_id == self.rental_out_loc)
        self.assertTrue(rental_out_pick)
        rental_in_pick = so.picking_ids.filtered(
            lambda p:
            p.location_id == self.rental_out_loc
            and p.location_dest_id == self.rental_in_loc)
        self.assertTrue(rental_in_pick)
        rental = self.env["sale.rental"].search([
            ("start_order_line_id", "=", sol.id)])
        self.assertTrue(rental)

        # Sell the same product/rental
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.test_partner
        with so_form.order_line.new() as line:
            line.product_id = self.test_rental_prod.rented_product_id
            line.product_uom_qty = 1
            line.sell_rental_id = rental
        so = so_form.save()
        sol = so.order_line
        # Raises an error because rented product is not sent yet
        with self.assertRaises(UserError):
            so.action_confirm()
        # Confirm the rental delivery and check the return which should
        # be cancelled
        rental_out_pick.action_assign()
        rental_out_pick.action_set_quantities_to_reservation()
        rental_out_pick.button_validate()
        so.action_confirm()
        self.assertEqual(rental_in_pick.state, "cancel")
