# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from odoo import exceptions


class TestProductSet(common.SavepointCase):
    """ Test Product set"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env['sale.order']
        cls.product_set_add = cls.env['product.set.add']

    def test_add_set(self):
        so = self.env.ref('sale.sale_order_6')
        count_lines = len(so.order_line)
        product_set = self.env.ref(
            'sale_product_set.product_set_i5_computer')
        # Simulation the opening of the wizard and adding a set on the
        # current sale order
        so_set = self.product_set_add.with_context(
            active_id=so.id).create({'product_set_id': product_set.id,
                                     'quantity': 2})
        so_set.add_set()
        # checking our sale order
        self.assertEqual(len(so.order_line), count_lines + 3)
        # check all lines are included
        for line in product_set.set_line_ids:
            order_line = so.order_line.filtered(
                lambda x: x.product_id == line.product_id
            )
            order_line.ensure_one()
            self.assertEqual(
                order_line.product_uom_qty, line.quantity * so_set.quantity
            )

        sequence = {}
        for line in so.order_line:
            sequence[line.product_id.id] = line.sequence
        # make sure sale order line sequence keep sequence set on set
        seq_line1 = sequence.pop(
            self.env.ref(
                "sale_product_set.product_set_line_computer_4"
            ).product_id.id)
        seq_line2 = sequence.pop(
            self.env.ref(
                "sale_product_set.product_set_line_computer_1"
            ).product_id.id)
        seq_line3 = sequence.pop(
            self.env.ref(
                "sale_product_set.product_set_line_computer_3"
            ).product_id.id)
        self.assertTrue(max([v for k, v in sequence.items()]) <
                        seq_line1 < seq_line2 < seq_line3)

    def test_add_set_on_empty_so(self):
        so = self.sale_order.create({
            'partner_id': self.ref('base.res_partner_1')})
        product_set = self.env.ref(
            'sale_product_set.product_set_i5_computer')
        so_set = self.product_set_add.with_context(
            active_id=so.id).create({'product_set_id': product_set.id,
                                     'quantity': 2})
        so_set.add_set()
        self.assertEqual(len(so.order_line), 3)

    def test_add_set_non_matching_partner(self):
        so = self.sale_order.create({
            'partner_id': self.ref('base.res_partner_1')})
        product_set = self.env.ref(
            'sale_product_set.product_set_i5_computer')
        product_set.partner_id = self.ref('base.res_partner_2')
        so_set = self.product_set_add.with_context(
            active_id=so.id).create({'product_set_id': product_set.id,
                                     'quantity': 2})
        with self.assertRaises(exceptions.ValidationError):
            so_set.add_set()

    def test_add_set_no_update_existing_products(self):
        so = self.sale_order.create({
            'partner_id': self.ref('base.res_partner_1')})
        product_set = self.env.ref(
            'sale_product_set.product_set_i5_computer')
        so_set = self.product_set_add.with_context(
            active_id=so.id).create({'product_set_id': product_set.id,
                                     'quantity': 2})
        so_set.add_set()
        self.assertEqual(len(so.order_line), 3)
        # if we run it again by default the wizard sums up quantities
        so_set.add_set()
        self.assertEqual(len(so.order_line), 6)
        # but we can turn it off
        so_set.skip_existing_products = True
        so_set.add_set()
        self.assertEqual(len(so.order_line), 6)

    def test_name(self):
        product_set = self.env.ref(
            'sale_product_set.product_set_i5_computer')
        # no ref
        product_set.name = 'Foo'
        product_set.ref = ''
        self.assertEqual(
            product_set.name_get(),
            [(product_set.id, 'Foo')]
        )
        # with ref
        product_set.ref = '123'
        self.assertEqual(
            product_set.name_get(),
            [(product_set.id, '[123] Foo')]
        )
        # with partner
        partner = self.env.ref('base.res_partner_1')
        product_set.partner_id = partner
        self.assertEqual(
            product_set.name_get(),
            [(product_set.id, '[123] Foo @ %s' % partner.name)]
        )
