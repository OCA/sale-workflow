# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TesSaleOrderInvoicingPickingFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.product = cls.env["product.product"].create(
            {"name": "Product test", "type": "product"}
        )
        cls.product_service = cls.env["product.product"].create(
            {"name": "Product Service Test", "type": "service"}
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "Partner 1 test"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Partner 2 test"})

    def create_sale_order(self, partner, qty, price_unit):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = partner
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = self.product
            soline_form.product_uom_qty = qty
            soline_form.price_unit = price_unit
        return so_form.save()

    def create_invoicing_wizard(
        self, order_ids, picking_ids, invoice_service_products=False
    ):
        return self.env["sale.advance.payment.inv"].create(
            {
                "sale_order_ids": order_ids,
                "advance_payment_method": "delivered",
                "stock_picking_ids": picking_ids,
                "inv_service_products": invoice_service_products,
            }
        )

    def test_invoice_single_sale_single_picking(self):

        # Create and validate sale order
        sale_order = self.create_sale_order(self.partner_1, 2, 2)
        sale_order.action_confirm()

        # Validate picking
        picking = sale_order.picking_ids
        self.assertTrue(picking)
        picking.move_ids.write({"quantity_done": 2})
        picking._action_done()

        # Create invoicing wizard related to the sale order
        # containing its picking.
        # Generate invoice
        wizard = self.create_invoicing_wizard([sale_order.id], [picking.id])
        wizard.create_invoices()
        sale_order.invoice_ids._compute_picking_ids()
        self.assertEqual(len(sale_order.invoice_ids), 1)
        self.assertEqual(
            sale_order.amount_untaxed, sale_order.invoice_ids[0].amount_untaxed
        )
        self.assertTrue(picking.invoiced)

    def test_invoice_single_sale_multiple_picking(self):

        # Create and validate sale order
        sale_order = sale_order = self.create_sale_order(self.partner_1, 2, 2)
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        self.assertTrue(picking)

        # Validate picking and generate backorder
        picking.move_ids.write({"quantity_done": 1})
        picking._action_done()
        self.assertEqual(len(sale_order.picking_ids), 2)

        # Create invoicing wizard related to the sale order
        # containing the validated picking.
        # Generate invoice
        wizard_1 = self.create_invoicing_wizard([sale_order.id], [picking.id])
        wizard_1.create_invoices()
        sale_order.invoice_ids._compute_picking_ids()
        self.assertEqual(len(sale_order.invoice_ids), 1)
        self.assertTrue(picking.invoiced)

        # Validate the backorder picking
        # Generate wizard related to the sale order
        # containint the validated backorder picking.
        # Generate invoice
        picking = sale_order.picking_ids.filtered(lambda a: not a.invoiced)
        self.assertEqual(len(picking), 1)
        picking.move_ids.write({"quantity_done": 1})
        picking._action_done()
        wizard_2 = self.create_invoicing_wizard([sale_order.id], [picking.id])
        wizard_2.create_invoices()
        sale_order.invoice_ids._compute_picking_ids()
        self.assertTrue(picking.invoiced)

        self.assertEqual(len(sale_order.invoice_ids), 2)
        for invoice in sale_order.invoice_ids:
            self.assertEqual(invoice.amount_untaxed, 2)

    def test_invoice_multiple_sales(self):

        # Create and validate the first sale order
        sale_order_1 = self.create_sale_order(self.partner_1, 2, 2)
        sale_order_1.action_confirm()
        picking_1 = sale_order_1.picking_ids
        self.assertTrue(picking_1)

        # Validate the picking related to the first order
        picking_1.move_ids.write({"quantity_done": 2})
        picking_1._action_done()

        # Create and validate the second sale order
        sale_order_2 = self.create_sale_order(self.partner_1, 2, 3)
        sale_order_2.action_confirm()
        picking_2 = sale_order_2.picking_ids
        self.assertTrue(picking_2)

        # Validate the picking related to the second order
        picking_2.move_ids.write({"quantity_done": 2})
        picking_2._action_done()

        # Generate wizard related to both sale orders
        # containint the pickings from them.
        # Generate invoice
        wizard = self.create_invoicing_wizard(
            [sale_order_1.id, sale_order_2.id], [picking_1.id, picking_2.id]
        )
        wizard.create_invoices()
        sale_order_1.invoice_ids._compute_picking_ids()
        sale_order_2.invoice_ids._compute_picking_ids()

        self.assertEqual(len(sale_order_1.invoice_ids), 1)
        self.assertEqual(len(sale_order_2.invoice_ids), 1)
        self.assertTrue(picking_1.invoiced)
        self.assertTrue(picking_2.invoiced)
        self.assertEqual(sale_order_1.invoice_ids, sale_order_2.invoice_ids)
        self.assertEqual(sale_order_1.invoice_ids.amount_untaxed, 10.0)

    def test_invoice_multiple_sales_multiple_clients(self):

        # Create and validate the first sales order
        sale_order_1 = self.create_sale_order(self.partner_1, 6, 1)
        sale_order_1.action_confirm()
        picking_1 = sale_order_1.picking_ids
        self.assertTrue(picking_1)

        # Validate picking from the first sale order and generate backorder
        picking_1.move_ids.write({"quantity_done": 2})
        picking_1._action_done()
        self.assertEqual(len(sale_order_1.picking_ids), 2)

        # Create and validate the second sales order
        sale_order_2 = self.create_sale_order(self.partner_1, 7, 2)
        sale_order_2.action_confirm()
        picking_2 = sale_order_2.picking_ids
        self.assertTrue(picking_2)

        # Validate picking from the second sale order and generate backorder
        picking_2.move_ids.write({"quantity_done": 3})
        picking_2._action_done()
        self.assertEqual(len(sale_order_2.picking_ids), 2)

        # Create and validate the third sales order
        sale_order_3 = self.create_sale_order(self.partner_2, 8, 3)
        sale_order_3.action_confirm()
        picking_3 = sale_order_3.picking_ids
        self.assertTrue(picking_3)

        # Validate picking from the third sale order and generate backorder
        picking_3.move_ids.write({"quantity_done": 4})
        picking_3._action_done()
        self.assertEqual(len(sale_order_3.picking_ids), 2)

        # Create and validate the fourth sales order
        sale_order_4 = self.create_sale_order(self.partner_2, 9, 4)
        sale_order_4.action_confirm()
        picking_4 = sale_order_4.picking_ids
        self.assertTrue(picking_4)

        # Validate picking from the fourth sale order and generate backorder
        picking_4.move_ids.write({"quantity_done": 5})
        picking_4._action_done()
        self.assertEqual(len(sale_order_4.picking_ids), 2)

        # Generate wizard related to all sale orders
        # containint all the validated pickings.
        # Generate invoice
        wizard = self.create_invoicing_wizard(
            [sale_order_1.id, sale_order_2.id, sale_order_3.id, sale_order_4.id],
            [picking_1.id, picking_2.id, picking_3.id, picking_4.id],
        )
        wizard.create_invoices()
        sale_order_1.invoice_ids._compute_picking_ids()
        sale_order_3.invoice_ids._compute_picking_ids()
        self.assertEqual(len(sale_order_1.invoice_ids), 1)
        self.assertEqual(len(sale_order_2.invoice_ids), 1)
        self.assertEqual(len(sale_order_3.invoice_ids), 1)
        self.assertEqual(len(sale_order_4.invoice_ids), 1)
        self.assertEqual(sale_order_1.invoice_ids, sale_order_2.invoice_ids)
        self.assertEqual(sale_order_3.invoice_ids, sale_order_4.invoice_ids)
        self.assertNotEqual(sale_order_1.invoice_ids, sale_order_3.invoice_ids)
        self.assertEqual(sale_order_2.invoice_ids.amount_untaxed, 8.0)
        self.assertEqual(sale_order_4.invoice_ids.amount_untaxed, 32.0)

        self.assertTrue(picking_1.invoiced)
        self.assertTrue(picking_2.invoiced)
        self.assertTrue(picking_3.invoiced)
        self.assertTrue(picking_4.invoiced)

        picking_backorder_1 = sale_order_1.picking_ids.filtered(
            lambda a: not a.invoiced
        )
        self.assertTrue(picking_backorder_1)
        picking_backorder_2 = sale_order_2.picking_ids.filtered(
            lambda a: not a.invoiced
        )
        self.assertTrue(picking_backorder_2)
        picking_backorder_3 = sale_order_3.picking_ids.filtered(
            lambda a: not a.invoiced
        )
        self.assertTrue(picking_backorder_3)
        picking_backorder_4 = sale_order_4.picking_ids.filtered(
            lambda a: not a.invoiced
        )
        self.assertTrue(picking_backorder_4)

        # Validate backorder pickings
        picking_backorder_1.move_ids.write({"quantity_done": 4})
        picking_backorder_1._action_done()
        picking_backorder_2.move_ids.write({"quantity_done": 4})
        picking_backorder_2._action_done()
        picking_backorder_3.move_ids.write({"quantity_done": 4})
        picking_backorder_3._action_done()
        picking_backorder_4.move_ids.write({"quantity_done": 4})
        picking_backorder_4._action_done()

        # Generate wizard related to all sale orders
        # containint all the backorder pickings.
        # Generate invoice
        wizard = self.create_invoicing_wizard(
            [sale_order_1.id, sale_order_2.id, sale_order_3.id, sale_order_4.id],
            [
                picking_backorder_1.id,
                picking_backorder_2.id,
                picking_backorder_3.id,
                picking_backorder_4.id,
            ],
        )
        wizard.create_invoices()

        self.assertEqual(len(sale_order_1.invoice_ids), 2)
        self.assertEqual(len(sale_order_2.invoice_ids), 2)
        self.assertEqual(len(sale_order_3.invoice_ids), 2)
        self.assertEqual(len(sale_order_4.invoice_ids), 2)
        self.assertEqual(sale_order_1.invoice_ids, sale_order_2.invoice_ids)
        self.assertEqual(sale_order_3.invoice_ids, sale_order_4.invoice_ids)
        self.assertNotEqual(sale_order_1.invoice_ids, sale_order_3.invoice_ids)
        self.assertEqual(sum(sale_order_1.invoice_ids.mapped("amount_untaxed")), 20.0)
        self.assertEqual(sum(sale_order_2.invoice_ids.mapped("amount_untaxed")), 20.0)
        self.assertEqual(sum(sale_order_3.invoice_ids.mapped("amount_untaxed")), 60.0)
        self.assertEqual(sum(sale_order_4.invoice_ids.mapped("amount_untaxed")), 60.0)
        self.assertFalse(sale_order_1.picking_ids.filtered(lambda a: not a.invoiced))
        self.assertFalse(sale_order_2.picking_ids.filtered(lambda a: not a.invoiced))
        self.assertFalse(sale_order_3.picking_ids.filtered(lambda a: not a.invoiced))
        self.assertFalse(sale_order_4.picking_ids.filtered(lambda a: not a.invoiced))

    def test_invoice_only_pickings_moves_multiple_products_types(self):
        """Checks for storable and service products.
        Only invoice the products from the picking of the first invoice
            (invoice_service_products= False)
        And the rest of products in the second invoice
            (invoice_service_products= True)
        """
        # Create and validate a sales order with multiple products
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_2
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = self.product
            soline_form.product_uom_qty = 7
            soline_form.price_unit = 2
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = self.product_service
            soline_form.product_uom_qty = 8
            soline_form.price_unit = 1
        sale_order = so_form.save()
        sale_order.action_confirm()
        picking_1 = sale_order.picking_ids
        self.assertTrue(picking_1)

        # Validate picking of the sale order and generate backorder
        picking_1.move_ids.write({"quantity_done": 3})
        picking_1._action_done()
        self.assertEqual(len(sale_order.picking_ids), 2)

        # Generate wizard related to the sale order
        # containint all the validated pickings.
        # Generate invoice
        wizard = self.create_invoicing_wizard(
            [sale_order.id],
            [picking_1.id, picking_1.id],
        )

        wizard.create_invoices()
        sale_order.invoice_ids._compute_picking_ids()
        self.assertEqual(len(sale_order.invoice_ids), 1)
        self.assertEqual(len(sale_order.invoice_ids), 1)
        self.assertEqual(sale_order.invoice_ids, sale_order.invoice_ids)
        self.assertEqual(sale_order.invoice_ids.amount_untaxed, 6.0)

        self.assertTrue(picking_1.invoiced)

        picking_backorder = sale_order.picking_ids.filtered(lambda a: not a.invoiced)
        self.assertTrue(picking_backorder)

        # Validate backorder pickings
        picking_backorder.move_ids.write({"quantity_done": 4})
        picking_backorder._action_done()

        # Generate wizard related to all sale orders
        # containint all the backorder pickings.
        # Generate invoice
        wizard = self.create_invoicing_wizard(
            [sale_order.id], [picking_backorder.id], True
        )
        wizard.create_invoices()

        self.assertEqual(len(sale_order.invoice_ids), 2)
        self.assertEqual(sum(sale_order.invoice_ids.mapped("amount_untaxed")), 22.0)
        self.assertFalse(sale_order.picking_ids.filtered(lambda a: not a.invoiced))

    def test_invoice_pickings_services_return(self):

        # Create and validate sale order containing a service product
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_2
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = self.product
            soline_form.product_uom_qty = 7
            soline_form.price_unit = 2
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = self.product_service
            soline_form.product_uom_qty = 2
            soline_form.price_unit = 1
        sale_order = so_form.save()
        sale_order.action_confirm()

        # Validate picking
        picking_1 = sale_order.picking_ids
        picking_1.move_ids.write({"quantity_done": 7})
        picking_1._action_done()

        # Return picking and validate
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking_1.ids,
                active_id=picking_1.ids[0],
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = 7.0
        stock_return_picking_action = stock_return_picking.create_returns()
        picking_2 = self.env["stock.picking"].browse(
            stock_return_picking_action["res_id"]
        )
        picking_2.move_ids.write({"quantity_done": 7})
        picking_2._action_done()

        # Generate invoices containing both pickings
        # Services are invoiced
        wizard = self.create_invoicing_wizard(
            [sale_order.id], [picking_1.id, picking_2.id], True
        )
        wizard.create_invoices()
        sale_order.invoice_ids._compute_picking_ids()

        self.assertEqual(len(sale_order.invoice_ids), 2)
        out_invoice = sale_order.invoice_ids.filtered(
            lambda a: a.move_type == "out_invoice"
        )
        out_refund_invoice = sale_order.invoice_ids.filtered(
            lambda a: a.move_type == "out_refund"
        )
        self.assertEqual(len(out_invoice), 1)
        self.assertEqual(len(out_refund_invoice), 1)
        self.assertEqual(out_invoice.amount_untaxed, 16.0)
        self.assertEqual(out_refund_invoice.amount_untaxed, 14.0)

    def test_invoice_pickings_services_return_generate_invoice(self):

        # Create and validate sale order containing a service product
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_2
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = self.product
            soline_form.product_uom_qty = 7
            soline_form.price_unit = 2
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = self.product_service
            soline_form.product_uom_qty = 2
            soline_form.price_unit = 1
        sale_order = so_form.save()
        sale_order.action_confirm()

        # Validate picking
        picking_1 = sale_order.picking_ids
        picking_1.move_ids.write({"quantity_done": 7})
        picking_1._action_done()

        # Return picking and validate
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking_1.ids,
                active_id=picking_1.ids[0],
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = 7.0
        stock_return_picking_action = stock_return_picking.create_returns()
        picking_2 = self.env["stock.picking"].browse(
            stock_return_picking_action["res_id"]
        )
        picking_2.move_ids.write({"quantity_done": 7})
        picking_2._action_done()

        # Generate invoices containing only the return picking
        # Services are invoiced
        wizard = self.create_invoicing_wizard([sale_order.id], [picking_2.id], True)
        wizard.create_invoices()
        sale_order.invoice_ids._compute_picking_ids()

        self.assertEqual(len(sale_order.invoice_ids), 2)
        out_invoice = sale_order.invoice_ids.filtered(
            lambda a: a.move_type == "out_invoice"
        )
        out_refund_invoice = sale_order.invoice_ids.filtered(
            lambda a: a.move_type == "out_refund"
        )
        self.assertEqual(len(out_invoice), 1)
        self.assertEqual(len(out_refund_invoice), 1)
        self.assertEqual(out_invoice.amount_untaxed, 2.0)
        self.assertEqual(out_refund_invoice.amount_untaxed, 14.0)
