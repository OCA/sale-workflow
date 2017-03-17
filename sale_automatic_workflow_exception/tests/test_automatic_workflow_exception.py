# -*- coding: utf-8 -*-
# © 2017 Today Akretion (http://www.akretion.com).
# @author  Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.sale_automatic_workflow.tests.test_automatic_workflow_base\
    import TestAutomaticWorkflowBase


class TestAutomaticWorkflowExcept(TestAutomaticWorkflowBase):

    def test_full_automatic(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        exception = self.env.ref('sale_exception.excep_no_zip')
        exception.active = True
        partner = self.env.ref('base.res_partner_1')
        partner.zip = False
        sale.partner_id = partner
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.workflow_process_id, workflow)
        self.progress()
        self.assertEqual(sale.state, 'draft')
        sale.ignore_exception = True
        self.progress()
        self.assertEqual(sale.state, u'sale')
