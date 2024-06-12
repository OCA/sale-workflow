# Copyright 2018 Tecnativa - David Vidal
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common, Form


class TestSaleStockPickingNote(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleStockPickingNote, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'type': 'product',
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'product_uom_qty': 1,
            })],
        })

    def test_01_sale_to_picking_note(self):
        """ Pass note to picking from SO """
        self.order.picking_note = "This note goes to the picking..."
        self.order.action_confirm()
        self.assertEqual(self.order.picking_ids[:1].note,
                         self.order.picking_note)

    def test_partner_default(self):
        """Propagate note from Partner to Sale Order."""
        # Arrange: Create a partner having a note
        partner = self.partner.copy(default={
            'default_picking_note': "Note",
        })
        order = self.order
        # pre-condition: The partner has a note but the order doesn't
        self.assertTrue(partner.default_picking_note)
        self.assertFalse(order.picking_note)

        # Act: Assign the partner to the order
        order_form = Form(order)
        order_form.partner_id = partner
        order_form.save()

        # Assert: The order has the same note as the partner
        self.assertEqual(
            partner.default_picking_note,
            order.picking_note,
        )
