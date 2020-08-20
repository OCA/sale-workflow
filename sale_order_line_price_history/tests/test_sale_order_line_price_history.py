# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleOrderLinePriceHistory(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env.ref('base.res_partner_1')
        cls.partner_2 = cls.env.ref('base.res_partner_2')
        cls.product = cls.env.ref('product.product_order_01')
        cls.sale_order_1 = cls.env['sale.order'].create({
            'partner_id': cls.partner_1.id,
        })
        # Two sale orders confirmed and with different partners
        cls.sale_order_line_1 = cls.env['sale.order.line'].create({
            'order_id': cls.sale_order_1.id,
            'name': cls.product.name,
            'product_id': cls.product.id,
            'product_uom_qty': 2,
            'product_uom': cls.product.uom_id.id,
            'price_unit': 10,
            'discount': 5,
        })
        cls.sale_order_1.action_confirm()
        cls.sale_order_2 = cls.env['sale.order'].create({
            'partner_id': cls.partner_2.id,
        })
        cls.sale_order_line_2 = cls.env['sale.order.line'].create({
            'order_id': cls.sale_order_2.id,
            'name': cls.product.name,
            'product_id': cls.product.id,
            'product_uom_qty': 2,
            'product_uom': cls.product.uom_id.id,
            'price_unit': 20,
        })
        cls.sale_order_2.action_confirm()
        # Another sale orders with the same partner of cls.sale_order_2
        cls.sale_order_3 = cls.env['sale.order'].create({
            'partner_id': cls.partner_2.id,
        })
        cls.sale_order_line_3 = cls.env['sale.order.line'].create({
            'order_id': cls.sale_order_3.id,
            'name': cls.product.name,
            'product_id': cls.product.id,
            'product_uom_qty': 2,
            'product_uom': cls.product.uom_id.id,
            'price_unit': 30,
        })

    def launch_wizard(self, active_id):
        wizard_obj = self.env['sale.order.line.price.history']
        wizard = wizard_obj.with_context(active_id=active_id).create({})
        wizard._onchange_partner_id()
        return wizard

    def test_onchange_partner_id(self):
        # Create a wizard from self.sale_order_line_3. Only one history line
        # should be shown and should be associated with self.sale_order_line_2
        wizard = self.launch_wizard(self.sale_order_line_3.id)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.sale_order_line_id,
                         self.sale_order_line_2)
        self.assertEqual(wizard.line_ids.price_unit, 20)
        # Set partner to False. Two history lines should be shown and
        # they should be associated with self.sale_order_line_1
        # and self.sale_order_line_2
        wizard.partner_id = False
        wizard._onchange_partner_id()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(
            set(wizard.line_ids.mapped('sale_order_line_id.price_unit')),
            set(list([10.0, 20.0])))

    def test_onchange_partner_id_include_quotations(self):
        # Another sale orders with the same partner of cls.sale_order_2
        # and cls.sale_order_3
        self.sale_order_4 = self.env['sale.order'].create({
            'partner_id': self.partner_2.id,
        })
        self.sale_order_line_4 = self.env['sale.order.line'].create({
            'order_id': self.sale_order_4.id,
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom_qty': 2,
            'product_uom': self.product.uom_id.id,
            'price_unit': 40,
        })
        # Create a wizard from self.sale_order_line_4. Only one history line
        # should be shown and should be associated with self.sale_order_line_2
        wizard = self.launch_wizard(self.sale_order_line_4.id)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.sale_order_line_id,
                         self.sale_order_line_2)
        # If include_quotations is checked two history lines should be shown
        # and they should be associated with self.sale_order_line_2
        # and self.sale_order_line_3
        wizard.include_quotations = True
        wizard._onchange_partner_id()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(wizard.line_ids.mapped('sale_order_line_id'),
                         self.sale_order_line_2 | self.sale_order_line_3)

    def test_onchange_partner_id_include_commercial_partner(self):
        # Another sale orders with a partner child of cls.sale_order_2
        self.sale_order_4 = self.env['sale.order'].create({
            'partner_id': self.ref('base.res_partner_address_31'),
        })
        self.sale_order_line_4 = self.env['sale.order.line'].create({
            'order_id': self.sale_order_4.id,
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom_qty': 2,
            'product_uom': self.product.uom_id.id,
            'price_unit': 40,
        })
        # Create a wizard from self.sale_order_line_4. As
        # include_commercial_partner si checked by default, one history line
        # should be shown and associated with self.sale_order_line_2
        wizard = self.launch_wizard(active_id=self.sale_order_line_4.id)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.sale_order_line_id,
                         self.sale_order_line_2)
        # Uncheck include_commercial_partner and Empty sale history
        # should be shown.
        wizard.include_commercial_partner = False
        wizard._onchange_partner_id()
        self.assertFalse(wizard.line_ids)

    def test_action_set_price(self):
        # Create a wizard from self.sale_order_line_3.
        wizard = self.launch_wizard(active_id=self.sale_order_line_3.id)
        self.assertEqual(self.sale_order_line_3.price_unit, 30)
        # Set price of the history line shown.
        wizard.line_ids.action_set_price()
        self.assertEqual(self.sale_order_line_3.price_unit, 20)
        self.assertEqual(self.sale_order_line_3.discount, 0)
        # Create a wizard from self.sale_order_line_3 again.
        wizard = self.launch_wizard(active_id=self.sale_order_line_3.id)
        wizard.partner_id = False
        wizard._onchange_partner_id()
        # Find the history line with price_unit == 10 and set this price
        history_line = wizard.line_ids.filtered(lambda r: r.price_unit == 10)
        history_line.action_set_price()
        self.assertEqual(self.sale_order_line_3.price_unit, 10)
        self.assertEqual(self.sale_order_line_3.discount, 5)
