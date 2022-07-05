# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from lxml import etree


class TestPartnerContactSaleInfoPropagation(TransactionCase):

    def setUp(self):
        super(TestPartnerContactSaleInfoPropagation, self).setUp()
        self.partner_model = self.env['res.partner']
        self.parent_company = self.partner_model.create({
            'name': 'Parent company',
            'company_type': 'company',
            'user_id': self.ref('base.user_demo'),
            'team_id': self.ref('sales_team.crm_team_1'),
        })

    def check_same_user_id_team_id(self, parent, child):
        self.assertEqual(parent.user_id, child.user_id)
        self.assertEqual(parent.team_id, child.team_id)

    def test_create_partner_child(self):
        partner_child = self.partner_model.create({
            'name': 'Parent child',
            'parent_id': self.parent_company.id,
        })
        self.check_same_user_id_team_id(self.parent_company, partner_child)

    def test_write_parent_company(self):
        partner_child = self.partner_model.create({
            'name': 'Parent child',
            'parent_id': self.parent_company.id,
        })
        self.parent_company.write({
            'user_id': self.ref('base.demo_user0'),
            'team_id': self.ref('sales_team.team_sales_department'),
        })
        self.check_same_user_id_team_id(self.parent_company, partner_child)

        partner_child.write({'user_id': False, 'team_id': False})
        self.parent_company.write({
            'user_id': self.ref('base.user_demo'),
            'team_id': self.ref('sales_team.crm_team_1'),
        })
        self.check_same_user_id_team_id(self.parent_company, partner_child)

    def test_onchange_parent_id_with_values_false(self):
        partner_child = self.partner_model.create({'name': 'Parent child'})
        partner_child.write({'parent_id': self.parent_company.id})
        onchange_result = partner_child.onchange_parent_id()
        self.assertEqual(onchange_result['value']['user_id'],
                         self.parent_company.user_id)
        self.assertEqual(onchange_result['value']['team_id'],
                         self.parent_company.team_id)

    def test_fields_view_get(self):
        # self.partner_model.fields_view_get(view_id=self.env.ref('test_new_api.discussion_form'))
        partner_xml = etree.XML(self.partner_model.fields_view_get()['arch'])
        partner_field = partner_xml.xpath("//field[@name='child_ids']")[0]
        context = partner_field.attrib.get("context", "{}")
        sub_ctx = "{'default_user_id': user_id, 'default_team_id': team_id,"
        self.assertIn(sub_ctx, context)
