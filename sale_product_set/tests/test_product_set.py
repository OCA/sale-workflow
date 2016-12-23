# -*- coding: utf-8 -*-
from odoo.tests import common


class test_product_set(common.TransactionCase):
    """ Test Product set"""

    def setUp(self):
        super(test_product_set, self).setUp()
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
        self.assertEquals(len(so.order_line), count_lines + 3)
        # untaxed_amount + ((147*1)+(2100*1)+(85*2)) * 2
        self.assertEquals(so.amount_untaxed, untaxed_amount + 4834.0)
        self.assertEquals(so.amount_tax, tax_amount + 0)  # without tax
        self.assertEquals(so.amount_total, total_amount + 4834.0)
        sequence = {}
        for line in so.order_line:
            sequence[line.product_id.id] = line.sequence
            for set_line in product_set.set_line_ids:
                if line.product_id.id == set_line.product_id.id:
                    self.assertEquals(line.product_id.name,
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
        self.assertTrue(max([v for k, v in sequence.iteritems()]) <
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
        self.assertEquals(len(so.order_line), 3)
