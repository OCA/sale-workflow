from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    primeship_ids = fields.One2many(
        comodel_name="sale.primeship",
        inverse_name="partner_id",
        required=True,
    )

    active_primeship = fields.Boolean(
        string="Active Primeship", compute="_compute_active_primeship", store=True
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
