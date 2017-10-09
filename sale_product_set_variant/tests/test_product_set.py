# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions
from odoo.tests import common


class ProductSetTestCase(common.TransactionCase):
    """ Test Product set"""

    def setUp(self):
        super(ProductSetTestCase, self).setUp()
        self.sale_order = self.env['sale.order']
        self.product_set_add = self.env['product.set.add']

    def _get_wizard(self, so, product_set):
        so_set = self.product_set_add.with_context(
            active_id=so.id).create({'product_set_id': product_set.id, })
        so_set._onchange_product_set_id()
        return so_set

    def test_add_set(self):
        so = self.env.ref('sale.sale_order_6')
        count_lines = len(so.order_line)

        product_set = self.env.ref(
            'sale_product_set_variant.product_set_i5_computer')
        # Simulation the opening of the wizard and adding a set on the
        # current sale order
        so_set = self._get_wizard(so, product_set)
        so_set.add_set()
        # checking our sale order
        self.assertEqual(len(so.order_line), count_lines + 2)
        self.assertAlmostEqual(so.amount_untaxed, 2300.4)
        self.assertAlmostEqual(so.amount_tax, 0)
        self.assertAlmostEqual(so.amount_total, 2300.4)

    def test_no_variants(self):
        so = self.sale_order.create({
            'partner_id': self.ref('base.res_partner_1')})
        product_set = self.env.ref(
            'sale_product_set_variant.product_set_i3_computer')
        so_set = self._get_wizard(so, product_set)
        with self.assertRaises(exceptions.UserError):
            so_set.add_set()
        product_set.set_line_ids[0].product_variant_ids = [
            (4, self.env.ref('product.product_product_4b').id)
        ]
        so_set = self._get_wizard(so, product_set)
        so_set.add_set()
        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.amount_untaxed, 750)
        self.assertEqual(so.amount_tax, 0)
        self.assertEqual(so.amount_total, 750)
