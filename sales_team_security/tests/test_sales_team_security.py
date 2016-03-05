# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common
from ..hooks import assign_contacts_team
from lxml import etree


class TestSalesTeamSecurity(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSalesTeamSecurity, cls).setUpClass()
        cls.section = cls.env['crm.case.section'].create({
            'name': 'Test section',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'section_id': cls.section.id,
        })

    def test_onchange_parent_id(self):
        res = self.env['res.partner'].onchange_address(True, self.partner.id)
        self.assertEqual(res['value']['section_id'], self.section.id)

    def test_assign_contacts_team(self):
        contact = self.env['res.partner'].create({
            'name': 'Test contact',
            'parent_id': self.partner.id,
            'section_id': False,
        })
        assign_contacts_team(self.env.cr, self.env.registry)
        contact.refresh()
        self.assertEqual(contact.section_id, self.partner.section_id)

    def test_partner_fields_view_get(self):
        res = self.env['res.partner'].fields_view_get(
            view_id=self.ref('base.view_partner_form'))
        eview = etree.fromstring(res['arch'])
        xml_fields = eview.xpath("//field[@name='child_ids']")
        self.assertTrue(xml_fields)
        self.assertTrue(
            'default_section_id' in xml_fields[0].get('context', ''))
