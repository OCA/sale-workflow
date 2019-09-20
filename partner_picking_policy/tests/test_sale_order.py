# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    """
    Tests for sale.order
    """

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.sale_obj = self.env['sale.order']
        self.values_obj = self.env['ir.values']
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref('product.product_product_4')

    def _create_sale_order(self, partner):
        """
        Create a new SO for the given partner
        :param partner: res.partner recordset
        :return: sale.order recordset
        """
        values = {
            'partner_id': partner.id,
            'order_line': [
                (0, False, {
                    'product_id': self.product.id,
                }),
            ],
        }
        return self.sale_obj.create(values)

    def _edit_settings(self, picking_policy):
        """
        Edit the default picking policy
        :param picking_policy: str
        :return: bool
        """
        model_so = self.sale_obj._name
        pick_policy_field = "picking_policy"
        self.values_obj.sudo().set_default(
            model_so, pick_policy_field, picking_policy)
        default_pick_policy = self.values_obj.get_default(
            model_so, pick_policy_field)
        self.assertEqual(picking_policy, default_pick_policy)
        return True

    def test_picking_policy_on_customer(self):
        """
        Scenario to test:
        - Define a picking policy on the partner
        - Create a SO
        - Play the onchange
        - Check if the picking policy is correct

        Then
        Do the same without specify a picking policy on the partner
        and check if the default value is correct.

        Do these 2 again by using another value for picking policy
        :return:
        """
        picking_policies = ["direct", "one"]
        for picking_policy in picking_policies:
            # Set another picking policy as default value for SO.
            other_picking_policy = [
                p for p in picking_policies if p != picking_policies][0]
            self._edit_settings(other_picking_policy)
            self.partner.write({
                'picking_policy': picking_policy,
            })
            # Ensure the write is correctly done
            self.assertEqual(self.partner.picking_policy, picking_policy)
            sale_order = self._create_sale_order(partner=self.partner)
            sale_order.onchange_partner_id()
            self.assertEqual(sale_order.picking_policy, picking_policy)
        return

    def test_picking_policy_in_settings(self):
        """
        Scenario to test:
        - Define a picking policy on the partner
        - Create a SO
        - Play the onchange
        - Check if the picking policy is correct

        Then
        Do the same without specify a picking policy on the partner
        and check if the default value is correct.

        Do these 2 again by using another value for picking policy
        :return:
        """
        picking_policies = ["direct", "one"]
        self.partner.write({
            'picking_policy': False,
        })
        for picking_policy in picking_policies:
            # Set another picking policy as default value for SO.
            self._edit_settings(picking_policy)
            # Ensure it still empty
            self.assertFalse(self.partner.picking_policy)
            sale_order = self._create_sale_order(partner=self.partner)
            sale_order.onchange_partner_id()
            self.assertEqual(sale_order.picking_policy, picking_policy)
        return
