# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions
from odoo.tests import common


class ProductSetTestCase(common.TransactionCase):
    """ Test Product set"""

    # TODO: would be nice to refactor these tests use `Form` test mock.

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
        # check all lines are included
        for line in product_set.set_line_ids:
            order_line = so.order_line.filtered(
                lambda x: x.product_id == line.product_variant_ids[0]
            )
            order_line.ensure_one()
            self.assertEqual(
                order_line.product_uom_qty, line.quantity * so_set.quantity
            )

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
        # check all lines are included
        for line in product_set.set_line_ids:
            order_line = so.order_line.filtered(
                lambda x: x.product_id == line.product_variant_ids[0]
            )
            order_line.ensure_one()
            self.assertEqual(
                order_line.product_uom_qty, line.quantity * so_set.quantity
            )

    def _get_single_variant_tmpl(self):
        tmpl = self.env.ref(
            'sale_product_set_variant.product_template_single_variant')
        variant = tmpl.product_variant_ids[0]
        # somehow depending on which modules you have installed
        # and which policies are enabled
        # you can get some more variants here.
        # We don't care, let's make sure we have only one.
        tmpl.product_variant_ids.filtered(lambda x: x != variant).unlink()
        return tmpl

    def test_no_variants_fallback_to_single_variant(self):
        so = self.sale_order.create({
            'partner_id': self.ref('base.res_partner_1')})
        product_set = self.env.ref(
            'sale_product_set_variant.product_set_i3_computer')
        so_set = self._get_wizard(so, product_set)
        line = product_set.set_line_ids[0]
        # wipe it variants
        line.product_template_id = None
        line.product_variant_ids = None
        # set a template w/ only one variant
        tmpl = self._get_single_variant_tmpl()
        self.assertEqual(len(tmpl.product_variant_ids), 1)
        product_set.set_line_ids[0].product_template_id = tmpl
        so_set = self._get_wizard(so, product_set)
        so_set.add_set()
        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.order_line.product_id, tmpl.product_variant_ids[0])
        self.assertEqual(so.order_line.product_uom_qty,
                         product_set.set_line_ids[0].quantity)

    def test_onchange_product_template_id(self):
        so = self.env.ref('sale.sale_order_6')
        product_set = self.env.ref(
            'sale_product_set_variant.product_set_i5_computer')
        so_set = self._get_wizard(so, product_set)
        set_lines = so_set.set_line_ids
        self.assertEqual(len(set_lines.mapped("product_variant_ids")), 2)
        set_lines._onchange_product_template_id()
        # the template has more than one variant available
        # hence wizard lines variants are wiped out to force you to select one
        self.assertEqual(len(set_lines.mapped("product_variant_ids")), 0)
        # assign a template w/ one variant only
        tmpl = self._get_single_variant_tmpl()
        set_lines[0].product_template_id = tmpl
        set_lines._onchange_product_template_id()
        # the default variant is selected
        self.assertEqual(len(set_lines.mapped("product_variant_ids")), 1)
        self.assertEqual(
            set_lines.mapped("product_variant_ids"), tmpl.product_variant_ids)

    def test_onchange_product_set_id(self):
        so = self.env.ref('sale.sale_order_6')
        product_set = self.env.ref(
            'sale_product_set_variant.product_set_i5_computer')
        # no template
        product_set.set_line_ids[0].product_template_id = None
        with self.assertRaises(exceptions.ValidationError):
            self._get_wizard(so, product_set)
