# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sale_country_ids = fields.Many2many(
        comodel_name="res.country",
        string="Sale Order Countries",
        relation="warehouse_sale_country_rel",
    )
    sale_state_ids = fields.Many2many(
        string="Sale Order States",
        comodel_name="res.country.state",
        compute="_compute_sale_state_ids",
        store=True,
        readonly=False,
        domain="[('country_id', 'in', sale_country_ids)]",
        relation="warehouse_sale_state_rel",
    )

    @api.depends("sale_country_ids")
    def _compute_sale_state_ids(self):
        for warehouse in self:
            sale_state_ids = self.sale_state_ids.filtered(
                lambda state: state.country_id.id in self.sale_country_ids.ids
            )
            warehouse.sale_state_ids = [(6, 0, sale_state_ids.ids)]

    def warehouses_by_country_state(self, partner):
        return self.filtered(lambda w: w._match_country_state(partner))

    def _match_country_state(self, partner):
        self.ensure_one()
        return (
            self.sale_country_ids
            and partner.country_id.id in self.sale_country_ids.ids
            and (
                not self.sale_state_ids
                or partner.state_id.id in self.sale_state_ids.ids
            )
        )
