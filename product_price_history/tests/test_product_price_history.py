# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestProductPriceHistory(common.TransactionCase):

    def setUp(self):
        super(TestProductPriceHistory, self).setUp()
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.pph_model = self.env['product.price.history']
        self.plph_model = self.env['product.lst.price.history']
        self.attribute_model = self.env['product.attribute']
        self.attribute_price_model = self.env['product.attribute.price']
        self.attribute_value_model = self.env['product.attribute.value']

        self.att_color = self.attribute_model.create({
            'name': 'color_test'
        })
        self.att_color_blue = self.attribute_value_model.create({
            'name': 'Blue',
            'attribute_id': self.att_color.id,
        })

        self.att_color_red = self.attribute_value_model.create({
            'name': 'Red',
            'attribute_id': self.att_color.id,
        })

        self.product_tmpl = self.product_tmpl_model.create({
            'name': 'Product Template',
            'list_price': 1500,
            'standard_price': 1400,
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': self.att_color.id,
                    'value_ids': [
                        (6, 0, (self.att_color_blue + self.att_color_red).ids)
                    ],
                })],
        })
        self.attribute_price_model.create({
            'product_tmpl_id': self.product_tmpl.id,
            'price_extra': 100,
            'value_id': self.att_color_blue.id
        })
        self.attribute_price_model.create({
            'product_tmpl_id': self.product_tmpl.id,
            'price_extra': 200,
            'value_id': self.att_color_red.id
        })
        self.product_blue = self.product_tmpl.product_variant_ids.filtered(
            lambda x: x.attribute_value_ids == self.att_color_blue)
        self.product_red = self.product_tmpl.product_variant_ids.filtered(
            lambda x: x.attribute_value_ids == self.att_color_red)

    def test_product_lst_price_history(self):

        self.product_tmpl.view_product_lst_price_history()
        self.product_tmpl.view_product_price_history()
        self.product_blue.view_product_lst_price_history()
        self.product_blue.view_product_price_history()

        lst_price_history = self.plph_model.search(
            [('product_id', 'in', self.product_tmpl.product_variant_ids.ids)])
        lst_price_history_blue = self.plph_model.search(
            [('product_id', '=', self.product_blue.id)])
        self.assertEqual(
            len(lst_price_history),
            2,
            'Too many records in the history.'
        )
        self.assertEqual(
            lst_price_history_blue.lst_price,
            self.product_blue.lst_price,
            'Sale price are not historicized proper.'
        )
        self.product_tmpl.list_price = 1400
        lst_price_history = self.plph_model.search(
            [('product_id', 'in', self.product_tmpl.product_variant_ids.ids)])
        self.assertEqual(
            len(lst_price_history),
            4,
            'Too many records in the history.'
        )

        lst_price_history_red = self.plph_model.search(
            [('product_id', '=', self.product_red.id)], limit=1)
        if lst_price_history_red:
            self.assertEqual(
                lst_price_history_red.lst_price,
                self.product_red.lst_price,
                'Sale price are not historicized proper.'
            )
