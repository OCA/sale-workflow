# © 2017 - Today Akretion (http://www.akretion.com).
# © 2020 Opener B.V. (https://opener.amsterdam).
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from mock import patch

from odoo.addons.sale_automatic_workflow.tests.test_automatic_workflow_base\
    import TestAutomaticWorkflowBase
from odoo.addons.sale_exception.models.sale import SaleOrder
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class TestAutomaticWorkflowExcept(TestAutomaticWorkflowBase):

    def test_automatic_workflow_exception(self):
        """ Orders with exceptions are excluded from the automatic workflow
        """
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

        # Call action_confirm() once to assert the exceptions on the sale
        # order.
        self.assertFalse(sale.exception_ids)
        sale.action_confirm()
        self.assertTrue(sale.exception_ids)
        self.assertEqual(sale.state, 'draft')

        def side_effect_action_confirm(self):
            """ Mock method that raises in the case of exceptions """
            for sale in self:
                if sale.exception_ids and not sale.ignore_exception:
                    raise ValidationError(
                        _('Sales with exceptions detected'))
            return super(SaleOrder, self).action_confirm()

        # To test if progress() calls action_confirm for our order once its
        # exceptions have been detected, our side effect will raise an
        # exception if that is the case
        with self.assertRaisesRegexp(ValidationError, 'Sales with exceptions'):
            with patch.object(
                    SaleOrder, 'action_confirm',
                    side_effect=side_effect_action_confirm, autospec=True):
                with self.env.cr.savepoint():
                    sale.action_confirm()

        # If our sale order is filtered out by progress(), our side effect
        # will not raise
        with patch.object(
                SaleOrder, 'action_confirm',
                side_effect=side_effect_action_confirm, autospec=True):
            self.progress()
        self.assertEqual(sale.state, 'draft')

        # Now ignore exceptions on our order. We expect progress() to
        # include it and confirm it
        sale.ignore_exception = True
        self.progress()
        self.assertEqual(sale.state, 'sale')
