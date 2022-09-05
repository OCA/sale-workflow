# Copyright 2021 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# @author: Julien Coux <julien.coux@camptocamp.com>
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from ..utils import roundTime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date_end = fields.Datetime(
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )
    seasonal_config_id = fields.Many2one(
        string="Product seasonal configuration",
        comodel_name="seasonal.config",
        default=lambda self: self._default_seasonal_config_id(),
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )
    season_allowed_product_ids = fields.Many2many(
        string="Season allowed products",
        comodel_name="product.product",
        column1="sale_id",
        column2="product_id",
        compute="_compute_season_allowed_product_ids",
    )

    def _default_seasonal_config_id(self):
        return self.env.user.company_id.default_seasonal_config_id

    def _get_allowed_product_ids(self, date):
        self.ensure_one()
        product_ids = []
        if date:
            config_lines = self.mapped("seasonal_config_id.line_ids").filtered(
                lambda l: l.is_sale_ok(date)
            )
            for config_line in config_lines:
                if config_line.product_id:
                    product_ids.append(config_line.product_id.id)
                else:
                    product_ids.extend(
                        config_line.product_template_id.product_variant_ids.ids
                    )
        return product_ids

    @api.depends("commitment_date", "seasonal_config_id.line_ids")
    def _compute_season_allowed_product_ids(self):
        for sale in self:
            value = [(5, 0)]
            if sale.commitment_date:
                product_ids = sale._get_allowed_product_ids(sale.commitment_date)
                value = [(6, 0, product_ids)]
            sale.season_allowed_product_ids = value

    def _round_dates(self):
        """Round dates to have a meaningful comparison time frame."""
        # TODO: make rounding factor configurable (see ROADMAP)
        if self.commitment_date:
            commitment_date = roundTime(dt=self.commitment_date, minutes=5)
            if self.commitment_date != commitment_date:
                self.commitment_date = commitment_date
        if self.commitment_date_end:
            commitment_date_end = roundTime(dt=self.commitment_date_end, minutes=5)
            if self.commitment_date_end != commitment_date_end:
                self.commitment_date_end = commitment_date_end

    @api.model
    def create(self, vals):
        sale = super().create(vals)
        if sale.commitment_date:
            sale._round_dates()
        return sale

    def write(self, vals):
        result = super().write(vals)
        if "commitment_date" in vals or "commitment_date_end" in vals:
            for sale in self:
                sale._round_dates()
        return result

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        res = super()._onchange_commitment_date()
        if self.commitment_date:
            self._round_dates()
            self.commitment_date_end = self.commitment_date
        return res

    @api.onchange("commitment_date_end")
    def _onchange_commitment_date_end(self):
        if self.commitment_date_end:
            self._round_dates()

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        self._update_seasonal_config(self.partner_id)
        return res

    def _update_seasonal_config(self, partner):
        commercial_partner = partner.commercial_partner_id
        # config
        config = partner.seasonal_config_id or commercial_partner.seasonal_config_id
        self.seasonal_config_id = config or self._default_seasonal_config_id()
