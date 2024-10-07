# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.secondary_uom_1 = cls.env['product.secondary.unit'].create(
            {'name': 'Unit 1'})
        cls.secondary_uom_2 = cls.env['product.secondary.unit'].create(
            {'name': 'Unit 2'})
        cls.secondary_uom_3 = cls.env['product.secondary.unit'].create(
            {'name': 'Unit 3'})
        cls.product_template_1 = cls.env['product.template'].create({
            'name': 'Test Product',
            'product_variant_ids': [(0, 0,
                                     {'name': 'Test Variant',
                                      'sale_secondary_uom_id':
                                          cls.secondary_uom_1.id})]
        })
        cls.product_template_2 = cls.env['product.template'].create({
            'name': 'Test Product',
            'product_variant_ids': [
                (0, 0, {'name': 'Test Variant 1',
                        'sale_secondary_uom_id': cls.secondary_uom_1.id}),
                (0, 0, {'name': 'Test Variant 2',
                        'sale_secondary_uom_id': cls.secondary_uom_2.id})
            ]
        })
        cls.product_template_3 = cls.env['product.template'].create({
            'name': 'Test Product',
            'product_variant_ids': [(0, 0, {'name': 'Test Variant'})]
        })
        cls.product_template_4 = cls.env['product.template'].create({
            'name': 'Test Product',
            'product_variant_ids': [
                (0, 0, {'name': 'Test Variant 1',
                        'sale_secondary_uom_id': cls.secondary_uom_1.id}),
                (0, 0, {'name': 'Test Variant 2',
                        'sale_secondary_uom_id': cls.secondary_uom_1.id})
            ]
        })

    def create_sets_sale_secondary_uom_id_for_single_variant(self):
        self.assertEqual(
            self.product_template_1.sale_secondary_uom_id.name, 'Unit 1')

    def create_does_not_set_sale_secondary_uom_id_for_multiple_variants(self):
        self.assertFalse(self.product_template_2.sale_secondary_uom_id)

    def create_sets_sale_secondary_uom_id_for_multiple_variants_with_same_uom(
            self):
        self.assertEqual(
            self.product_template_4.sale_secondary_uom_id.name, 'Unit 1')

    def inverse_sale_secondary_uom_id_updates_variants_correctly(self):
        self.product_template_3.sale_secondary_uom_id = self.secondary_uom_3
        self.product_template_3._inverse_sale_secondary_uom_id()
        self.assertEqual(
            self.product_template_3.product_variant_ids.sale_secondary_uom_id,
            self.secondary_uom_3)

    def onchange_sale_secondary_uom_id_warns_on_distinct_uoms(self):
        warning = self.product_template_2.onchange_sale_secondary_uom_id()
        self.assertIn('warning', warning)
        self.assertIn('Product variants have distinct sale secondary uom',
                      warning['warning']['message'])

    def create_sets_sale_secondary_uom_id_for_variant_with_no_uom(self):
        product_template = self.env['product.template'].create({
            'name': 'Test Product',
            'product_variant_ids': [(0, 0, {'name': 'Test Variant'})]
        })
        self.assertFalse(product_template.sale_secondary_uom_id)
