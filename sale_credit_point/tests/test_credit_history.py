# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHistory(TransactionCase):

    def setUp(self):
        super().setUp()
        self.history_model = self.env["credit.point.history"]
        self.partner = self.env['res.partner'].with_context(
            tracking_disable=True
        ).create({'name': 'John Wizard'})
        self.wiz_model = self.env['wiz.manage.credit.point']
        self.wiz_vals = [
            {
                'operation': 'increase',
                'credit_point': 15,
                'comment': 'test'
            },
            {
                'operation': 'increase',
                'credit_point': 25,
                'comment': 'test'
            },
            {
                'operation': 'replace',
                'credit_point': 15,
                'comment': 'test'
            },
            {
                'operation': 'decrease',
                'credit_point': 5,
                'comment': 'test'
            },
            {
                'operation': 'decrease',
                'credit_point': 5,
                'comment': 'test',
            },
        ]

    def _run_wiz(self):
        for vals in self.wiz_vals:
            vals.update({
                'partner_ids': [(6, 0, self.partner.ids)]
            })
            wiz = self.wiz_model.new(vals)
            wiz.action_update_credit()

    def test_history_creation(self):
        self._run_wiz()
        history = self.history_model.sudo().search([])
        self.assertEqual(len(history), len(self.wiz_vals))

    def test_yearly_credit_increase(self):
        self._run_wiz()
        history = self.history_model.sudo().search([])
        history = history.filtered(
            lambda x: x.operation == 'increase' and
            x.partner_id == self.partner
        )
        self.assertEqual(len(history), 2)
        self.assertEqual(self.partner.yearly_point_increase,
                         sum(history.mapped("amount")))
        self.env.cr.execute("update credit_point_history set "
                            "create_date='1994-10-03 10:00:00' where id=%s",
                            (history[0].id,))
        self.partner._compute_yearly_point_increase()
        self.assertNotEqual(self.partner.yearly_point_increase,
                            sum(history.mapped("amount")))
        self.assertEqual(self.partner.yearly_point_increase, history[1].amount)
