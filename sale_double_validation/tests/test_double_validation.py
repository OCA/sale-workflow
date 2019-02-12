# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.sale.tests import test_sale_common


class TestSaleDoubleValidation(test_sale_common.TestCommonSaleNoChart):

    def test_one_step(self):
        self.user_employee.company_id.sudo().so_double_validation = 'one_step'
        so = self.env['sale.order'].sudo(self.user_employee).create({
            'partner_id': self.partner_customer_usd.id,
            'partner_invoice_id': self.partner_customer_usd.id,
            'partner_shipping_id': self.partner_customer_usd.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.product_map.items()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        # confirm quotation
        self.assertEquals(so.state, 'draft')

    def test_two_steps_under_limit(self):
        self.user_employee.company_id.sudo().so_double_validation = 'two_step'
        so = self.env['sale.order'].sudo(self.user_employee).create({
            'partner_id': self.partner_customer_usd.id,
            'partner_invoice_id': self.partner_customer_usd.id,
            'partner_shipping_id': self.partner_customer_usd.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.product_map.items()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        # confirm quotation
        self.assertEquals(so.state, 'draft')

    def test_two_steps_manager(self):
        self.user_employee.company_id.sudo().so_double_validation = 'two_step'
        self.user_employee.company_id.sudo().so_double_validation_amount = 10
        so = self.env['sale.order'].sudo(self.user_manager).create({
            'partner_id': self.partner_customer_usd.id,
            'partner_invoice_id': self.partner_customer_usd.id,
            'partner_shipping_id': self.partner_customer_usd.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.product_map.items()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        # confirm quotation
        self.assertEquals(so.state, 'draft')

    def test_two_steps_limit(self):
        self.user_employee.company_id.sudo().so_double_validation = 'two_step'
        self.user_employee.company_id.sudo().so_double_validation_amount = \
            sum([2 * p.list_price for (k, p) in self.product_map.items()])
        so = self.env['sale.order'].sudo(self.user_employee).create({
            'partner_id': self.partner_customer_usd.id,
            'partner_invoice_id': self.partner_customer_usd.id,
            'partner_shipping_id': self.partner_customer_usd.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.product_map.items()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        # confirm quotation
        self.assertEquals(so.state, 'to_approve')

    def test_two_steps_above_limit(self):
        self.user_employee.company_id.sudo().so_double_validation = 'two_step'
        self.user_employee.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation
        so = self.env['sale.order'].sudo(self.user_employee).create({
            'partner_id': self.partner_customer_usd.id,
            'partner_invoice_id': self.partner_customer_usd.id,
            'partner_shipping_id': self.partner_customer_usd.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.product_map.items()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        # confirm quotation
        self.assertEquals(so.state, 'to_approve')
        so.sudo(self.user_manager).action_approve()
        self.assertEquals(so.state, 'draft')

    @classmethod
    def setUpClass(cls):
        super(TestSaleDoubleValidation, cls).setUpClass()
        cls.setUpUsers()
        group_salemanager = cls.env.ref('sales_team.group_sale_manager')
        group_salesman = cls.env.ref('sales_team.group_sale_salesman')
        group_employee = cls.env.ref('base.group_user')
        cls.user_manager.write(
            {'groups_id': [(6, 0, [group_salemanager.id, group_employee.id])]}
        )
        cls.user_employee.write(
            {'groups_id': [(6, 0, [group_salesman.id, group_employee.id])]}
        )

        # set up accounts and products and journals
        cls.setUpClassicProducts()
