# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, exceptions, _


class ManageCreditPoint(models.TransientModel):
    _name = 'wiz.manage.credit.point'

    credit_point = fields.Integer(
        string='Points',
        required=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        required=True,
    )
    comment = fields.Text(
        string='Comment',
        required=True,
    )
    operation = fields.Selection(
        string="Type of operation",
        selection=[
            ("replace", "Replace"),
            ("increase", "Increase"),
            ("decrease", "Decrease"),
        ],
        required=True,
    )

    @api.multi
    def action_update_credit(self):
        self.ensure_one()
        if not self.comment:
            raise exceptions.UserError(
                _("A comment is needed to the update credit")
            )
        for partner in self.partner_ids:
            handler = getattr(partner, 'credit_point_' + self.operation)
            handler(self.credit_point, comment=self.comment)
