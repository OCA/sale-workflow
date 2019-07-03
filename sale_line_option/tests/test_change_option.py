# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestOptionCase(TransactionCase):
    def setUp(self):
        super(TestOptionCase, self).setUp()
        self.sale_line = self.env.ref(
            'sale_line_option.sale_order_line_option')
        self.sale_line.product_id_change()
        self.bom_config_1 = self.env.ref(
            'sale_line_option.bom_pc_assmb_option1')
        self.bom_config_2 = self.env.ref(
            'sale_line_option.bom_pc_assmb_option2')
        self.product_config_2 = self.env.ref(
            'sale_line_option.product_pc_assmb_option2')
        self.product_no_config = self.env.ref(
            'product.product_delivery_01')

    def test_default_product_qty(self):
        qties = {
            x.product_id: x.opt_default_qty
            for x in self.bom_config_1.bom_line_ids}
        for line in self.sale_line.option_ids:
            self.assertEqual(
                line.qty, qties[line.product_id],
                "Option qty error on product %s" % line.product_id.name)

    def test_option(self):
        self.assertEqual(len(self.sale_line.option_ids), 3)
        for option in self.sale_line.option_ids:
            self.assertEqual(option.product_id, option.bom_line_id.product_id)

    def test_change_product_with_option_refresh_option(self):
        self.sale_line.product_id = self.product_config_2
        self.sale_line.product_id_change()

        self.assertEqual(len(self.sale_line.option_ids), 2)

        bom_products = [
            x.product_id.name
            for x in self.bom_config_2.bom_line_ids
            if x.opt_default_qty > 0]

        self.assertEqual(
            set(self.sale_line.option_ids.mapped('product_id.name')),
            set(bom_products),
            "Bom and option products should be identical")

    def test_change_product_without_option_clear_option(self):
        self.sale_line.product_id = self.product_no_config
        self.sale_line.product_id_change()
        self.assertEqual(len(self.sale_line.option_ids), 0)

    def test_remove_bom_line_do_not_change_option(self):
        option = self.sale_line.option_ids[0]
        product = option.product_id
        line_price = option.line_price
        qty = option.qty

        option.bom_line_id.unlink()
        self.assertEqual(option.product_id, product)
        self.assertEqual(option.line_price, line_price)
        self.assertEqual(option.qty, qty)
        self.assertEqual(len(option.bom_line_id), 0)

    def test_search_component_of_product(self):
        components = self.env['product.product'].search([
            ('component_of_product_ids', '=', self.product_config_2.id)
            ])
        self.assertEqual(len(components), 2)

    def test_compute_component_of_product(self):
        product = self.env.ref('product.product_product_20')
        self.assertEqual(len(product.component_of_product_ids), 2)

    def test_confirm_sale_order(self):
        sale = self.sale_line.order_id
        sale.action_confirm()
        production = self.env['mrp.production'].search([
            ('lot_id', '=', self.sale_line.lot_id.id)
            ])
        self.assertEqual(len(production.move_raw_ids), 3)
        options = self.sale_line.option_ids
        lines = production.move_raw_ids
        for idx in [0, 1, 2]:
            self.assertEqual(lines[idx].product_id, options[idx].product_id)
            self.assertEqual(lines[idx].product_qty, options[idx].qty)

    def test_max_qty(self):
        option = self.sale_line.option_ids[0]
        option.qty = 20
        res = option.onchange_qty()
        self.assertIn('warning', res)
        self.assertEqual(res['warning']['title'], u'Error on quantity')

    def test_min_qty(self):
        option = self.sale_line.option_ids[0]
        option.bom_line_id.opt_min_qty = 1
        option.qty = 0
        res = option.onchange_qty()
        self.assertIn('warning', res)
        self.assertEqual(res['warning']['title'], u'Error on quantity')

    def test_onchange_sale_line_qty(self):
        # calling product_uom_change should keep the same price unit
        price_unit = self.sale_line.price_unit
        self.sale_line.product_uom_change()
        self.assertEqual(self.sale_line.price_unit, price_unit)

    # Test for fixing broken one2many
    # See issue here https://github.com/odoo/odoo/issues/17618

    # we have two issue linked to this bug
    # 1- the write is broken
    # 2- the onchange on sale order remove some option_ids on sale order line
    # This test try to simulate this case

    def test_write_one2many(self):
        # pass the option_ids like odoo do after running the onchange
        vals = {'option_ids': [(5,)]}
        for option in self.sale_line.option_ids:
            vals['option_ids'].append((4, option.id))
        self.sale_line.write(vals)

    def _get_sale_data(self):
        return self.env['sale.order']._convert_to_write(
            self.sale_line.order_id.read()[0])

    def _get_sale_line_data(self):
        return self.env['sale.order.line']._convert_to_write(
            self.sale_line.read()[0])

    def _get_option_data(self):
        return [
            self.env['sale.order.line.option']._convert_to_write(
                option.read()[0])
            for option in self.sale_line.option_ids]

    def test_one2many_onchange_issue_with_new_sale(self):
        vals = self._get_sale_data()
        vals['id'] = False
        line_vals = self._get_sale_line_data()
        line_vals['id'] = False
        line_vals['option_ids'] = []
        for option in self._get_option_data():
            option['id'] = False
            line_vals['option_ids'].append((0, 0, option))
        vals['order_line'] = [(0, 0, line_vals)]

        onchange = {
            u'order_line.option_ids': u'1',
            u'partner_id': u'1',
            u'order_line.currency_id': u''}
        res = self.env['sale.order'].onchange(vals, "partner_id", onchange)

        onchange_options = res['value']['order_line'][1][2]['option_ids']
        self.assertEqual(onchange_options, line_vals['option_ids'])

    def test_one2many_onchange_issue_with_existing_sale(self):
        vals = self._get_sale_data()
        line_vals = self._get_sale_line_data()
        line_vals['option_ids'] = []
        for option in self._get_option_data():
            line_vals['option_ids'].append((4, option['id'], False))
        line_vals['option_ids'].append(
            (0, 0, {'product_id': self.env.ref(
                'product.product_product_12').id}))
        vals['order_line'] = [(1, line_vals.pop('id'), line_vals)]

        onchange = {
            u'order_line.option_ids': u'1',
            u'partner_id': u'1',
            u'order_line.currency_id': u''}
        res = self.env['sale.order'].onchange(vals, "partner_id", onchange)

        onchange_options = res['value']['order_line'][1][2]['option_ids']
        self.assertEqual(onchange_options, line_vals['option_ids'])
