# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestSaleMergeDraftInvoice(TransactionCase):

    def setUp(self):
        super(TestSaleMergeDraftInvoice, self).setUp()
        self.users_obj = self.env['res.users']
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']

        # company
        self.company1 = self.env.ref('base.main_company')

        # groups
        self.group_user = self.env.ref('base.group_user')
        self.group_sale_merge_draft_invoice = self.env.ref(
            'sale_merge_draft_invoice.group_sale_merge_draft_invoice')
        self.group_sale = self.env.ref('sales_team.group_sale_manager')

        # users
        self.user1_id = self._create_user(
            'user_1', [self.group_sale], self.company1)
        self.user2_id = self._create_user(
            'user_2', [self.group_sale_merge_draft_invoice, self.group_sale],
            self.company1)

        # customer
        self.customer = self._create_customer('Test Customer')

        # product
        product_ctg = self._create_product_category()
        self.service_1 = self._create_product('test_product1',
                                              product_ctg)
        self.service_2 = self._create_product('test_product2',
                                              product_ctg)

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = self.users_obj.with_context({'no_reset_password': True}).\
            create({
                'name': 'Sale User',
                'login': login,
                'password': 'test',
                'email': 'test@yourcompany.com',
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, group_ids)]
            })
        return user.id

    def _create_customer(self, name):
        """Create a Partner."""
        return self.env['res.partner'].create({
            'name': name,
            'email': 'example@yourcompany.com',
            'customer': True,
            'phone': 123456,
            'currency_id': self.env.ref('base.EUR'),
        })

    def _create_product_category(self):
        product_ctg = self.env['product.category'].create({
            'name': 'test_product_ctg',
        })
        return product_ctg

    def _create_product(self, name, product_ctg):
        product = self.env['product.product'].create({
            'name': name,
            'categ_id': product_ctg.id,
            'type': 'service',
        })
        return product

    def _create_sale_order(self, user):
        so = self.sale_order_model.sudo(user).create({
            'partner_id': self.customer.id,
        })
        sol1 = self.sale_order_line_model.sudo(user).create({
            'product_id': self.service_1.id,
            'product_uom_qty': 1,
            'order_id': so.id
        })
        sol2 = self.sale_order_line_model.sudo(user).create({
            'product_id': self.service_2.id,
            'product_uom_qty': 2,
            'order_id': so.id
        })

        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 1
        sol2.qty_delivered = 2
        return so

    def _create_invoice_from_sale(self, sale, user, merge_option=False,
                                  force_merge=False):
        data = {'advance_payment_method': 'delivered'}
        if force_merge:
            data.update({'merge_draft_invoice': merge_option})
        payment = self.env['sale.advance.payment.inv'].sudo(user).create(data)
        sale_context = {
            'active_id': sale.id,
            'active_ids': sale.ids,
            'active_model': 'sale.order',
            'open_invoices': True,
        }
        res = payment.with_context(sale_context).sudo(user).create_invoices()
        invoice_id = self.env['account.invoice'].browse(res['res_id'])
        return invoice_id

    def test_create_invoice_case_1(self):
        """ A user that doesn't belong to the group
        group_sale_merge_draft_invoice from a company with the option
        of merging invoices activated creates two sales orders. """

        self.company1.sale_merge_draft_invoice = True
        self.assertEquals(self.company1.sale_merge_draft_invoice, True,
                          "The selection should be to merge invoices")
        so1 = self._create_sale_order(self.user1_id)
        inv1 = self._create_invoice_from_sale(so1, self.user1_id)
        self.assertEquals(inv1.state, 'draft',
                          "The invoice status should be 'draft'")
        so2 = self._create_sale_order(self.user1_id)
        inv2 = self._create_invoice_from_sale(so2, self.user1_id)
        self.assertEquals(inv2.state, 'draft',
                          "The invoice status should be 'draft'")
        # The result is one invoice with all the lines
        self.assertEquals(inv1, inv2, "The invoices should be the same.")

    def test_create_invoice_case_2(self):
        """ A user that doesn't belong to the group
        group_sale_merge_draft_invoice from a company without the option
        of merging invoices activated creates two sales orders. """

        self.company1.sale_merge_draft_invoice = False
        self.assertEquals(self.company1.sale_merge_draft_invoice, False,
                          "The selection should be not to merge invoices")
        so1 = self._create_sale_order(self.user1_id)
        inv1 = self._create_invoice_from_sale(so1, self.user1_id)
        self.assertEquals(inv1.state, 'draft',
                          "The invoice status should be 'draft'")
        so2 = self._create_sale_order(self.user1_id)
        inv2 = self._create_invoice_from_sale(so2, self.user1_id)
        self.assertEquals(inv2.state, 'draft',
                          "The invoice status should be 'draft'")
        # The result is two different invoices (one for each sale order)
        self.assertTrue(inv1 != inv2)

    def test_create_invoice_case_3(self):
        """ A user that belongs to the group
        group_sale_merge_draft_invoice from a company with the option
        of merging invoices activated creates two sales orders.
        In this case, the user does not want to merge them. """

        self.company1.sale_merge_draft_invoice = True
        self.assertEquals(self.company1.sale_merge_draft_invoice, True,
                          "The selection should be not to merge invoices")
        so1 = self._create_sale_order(self.user2_id)
        inv1 = self._create_invoice_from_sale(so1, self.user2_id, False, True)
        self.assertEquals(inv1.state, 'draft',
                          "The invoice status should be 'draft'")
        so2 = self._create_sale_order(self.user2_id)
        inv2 = self._create_invoice_from_sale(so2, self.user2_id, False, True)
        self.assertEquals(inv2.state, 'draft',
                          "The invoice status should be 'draft'")
        # The result is two different invoices (one for each sale order)
        self.assertTrue(inv1 != inv2)

    def test_create_invoice_case_4(self):
        """ A user that belongs to the group
        group_sale_merge_draft_invoice from a company without the option
        of merging invoices activated creates two sales orders.
        In this case, the user wants to merge them. """

        self.company1.sale_merge_draft_invoice = False
        self.assertEquals(self.company1.sale_merge_draft_invoice, False,
                          "The selection should be not to merge invoices")
        so1 = self._create_sale_order(self.user2_id)
        inv1 = self._create_invoice_from_sale(so1, self.user2_id, True, True)
        self.assertEquals(inv1.state, 'draft',
                          "The invoice status should be 'draft'")
        so2 = self._create_sale_order(self.user2_id)
        inv2 = self._create_invoice_from_sale(so2, self.user2_id, True, True)
        self.assertEquals(inv2.state, 'draft',
                          "The invoice status should be 'draft'")
        # The result is one invoice with all the lines
        self.assertEquals(inv1, inv2, "The invoices should be the same.")
