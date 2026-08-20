# Copyright 2021 Akretion France (http://www.akretion.com/)
# Copyright 2023 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    primeship_ids = fields.One2many(
        comodel_name="sale.primeship",
        inverse_name="partner_id",
        required=True,
    )

    # store True allow to filter on active_primeship.
    # There is a cron job to set it to False when the customer has no active
    # primeship anymore.
    active_primeship = fields.Boolean(
        compute="_compute_active_primeship",
        store=True,
    )
    primeship_count = fields.Integer(
        string="Primeships Count", compute="_compute_primeship_count"
    )

    @api.depends(
        "commercial_partner_id.primeship_ids",
        "commercial_partner_id.primeship_ids.current",
    )
    def _compute_active_primeship(self):
        for record in self:
            record.active_primeship = (
                record.commercial_partner_id.primeship_ids.filtered("current")
            )

    @api.depends("commercial_partner_id.primeship_ids")
    def _compute_primeship_count(self):
        for record in self:
            record.primeship_count = len(record.commercial_partner_id.primeship_ids)

    @api.model
    def _check_expired_primeships(self):
        self.with_context(
            active_test=False,
        ).search([("active_primeship", "=", True)])._compute_active_primeship()
