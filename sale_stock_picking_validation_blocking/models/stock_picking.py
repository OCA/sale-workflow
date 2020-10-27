# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    validation_blocked_by_so = fields.Boolean(
        related="sale_id.picking_validation_blocked",
        store=True,
        string="Validation Blocked by SO",
    )

    @api.depends("state", "is_locked", "validation_blocked_by_so")
    def _compute_show_validate(self):
        for picking in self:
            if picking.validation_blocked_by_so:
                picking.show_validate = False
            else:
                super(StockPicking, picking)._compute_show_validate()

    def button_validate(self):
        for picking in self:
            if picking.validation_blocked_by_so:
                raise ValidationError(
                    _("Validation is blocked by SO for picking %s" % picking.name)
                )
        return super(StockPicking, self).button_validate()
