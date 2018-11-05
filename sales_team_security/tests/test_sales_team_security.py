# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common
from ..hooks import post_init_hook
from lxml import etree


class TestSalesTeamSecurity(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env['crm.team'].create({
            'name': 'Test channel',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'team_id': cls.team.id,
        })

    def test_onchange_parent_id(self):
        contact = self.env['res.partner'].create({
            'name': 'Test contact',
            'parent_id': self.partner.id,
        })
        contact._onchange_parent_id_sales_team_security()
        self.assertEqual(contact.team_id, self.team)

    def test_assign_contacts_team(self):
        contact = self.env['res.partner'].create({
            'name': 'Test contact',
            'parent_id': self.partner.id,
            'team_id': False,
        })
        post_init_hook(self.env.cr, self.env.registry)
        contact.refresh()
        self.assertEqual(contact.team_id, self.partner.team_id)

    def test_partner_fields_view_get(self):
        res = self.env['res.partner'].fields_view_get(
            view_id=self.ref('base.view_partner_form')
        )
        eview = etree.fromstring(res['arch'])
        xml_fields = eview.xpath("//field[@name='child_ids']")
        self.assertTrue(xml_fields)
        self.assertTrue('default_team_id' in xml_fields[0].get('context', ''))
