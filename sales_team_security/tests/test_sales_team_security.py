# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common
from ..hooks import assign_contacts_team
# from lxml import etree


class TestSalesTeamSecurity(common.TransactionCase):
    def setUp(self):
        super(TestSalesTeamSecurity, self).setUp()
        self.section = self.env['crm.team'].create({
            'name': 'Test section',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'team_id': self.section.id,
        })

    def test_assign_contacts_team(self):
        contact = self.env['res.partner'].create({
            'name': 'Test contact',
            'parent_id': self.partner.id,
            'team_id': False,
        })
        assign_contacts_team(self.env.cr, self.env.registry)
        contact.refresh()
        self.assertEqual(contact.team_id, self.partner.team_id)
