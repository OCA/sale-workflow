# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestProductSet(common.TransactionCase):
    """ Test Product set"""

    def setUp(self):
        super(TestProductSet, self).setUp()
        self.sale_order = self.env['sale.order']
        self.product_set_add = self.env['product.set.add']

    def test_add_set(self):
        so = self.env.ref('sale.sale_order_6')
        count_lines = len(so.order_line)
        untaxed_amount = so.amount_untaxed
        tax_amount = so.amount_tax
        total_amount = so.amount_total

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
        # untaxed_amount + ((147*1*0.75)+(2100*1)+(85*2)) * 2
        # 0.75 due to a 25% discount on Custom Computer (kit) product
        self.assertEqual(so.amount_untaxed, untaxed_amount + 4760.5)
        self.assertEqual(so.amount_tax, tax_amount + 0)  # without tax
        self.assertEqual(so.amount_total, total_amount + 4760.5)
        sequence = {}
        for line in so.order_line:
            sequence[line.product_id.id] = line.sequence
            for set_line in product_set.set_line_ids:
                if line.product_id.id == set_line.product_id.id:
                    self.assertEqual(line.product_id.name,
                                     set_line.product_id.name)
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
