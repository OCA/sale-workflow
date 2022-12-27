# Copyright 2018-2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, fields, models

from ..models.point_history import POINT_OPERATIONS


class ManageCreditPoint(models.TransientModel):
    _name = "wiz.manage.credit.point"
    _description = "Wizard to Manage Credit Points"

    credit_point = fields.Integer(
        string="Points",
        required=True,
    )
    partner_ids = fields.Many2many(
        "res.partner",
        string="Partners",
        required=True,
    )
    comment = fields.Text(
        required=True,
    )
    operation = fields.Selection(
        string="Type of operation",
        selection=POINT_OPERATIONS,
        required=True,
    )

    def action_update_credit(self):
        self.ensure_one()
        if not self.comment:
            raise exceptions.UserError(_("A comment is needed to the update credit"))
        for partner in self.partner_ids:
            handler = getattr(partner, "credit_point_" + self.operation)
            handler(self.credit_point, comment=self.comment)
            partner.update_history(self.credit_point, self.operation, self.comment)
