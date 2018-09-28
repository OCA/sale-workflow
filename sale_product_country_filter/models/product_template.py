# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import safe_eval


class ProductTemplate(models.Model):

    _inherit = "product.template"

    tmpl_globally_allowed = fields.Boolean(
        string="Globally allowed",
        help="If there are no blacklisted countries, you must explicitly set "
             "the product as 'globally allowed'",
    )
    tmpl_blacklisted_countries_ids = fields.Many2many(
        "res.country", string="Blacklisted countries"
    )
    blacklisted_category_country_ids = fields.Many2many(
        'product.category',
        compute='_compute_blacklisted_category_country_ids'
    )

    @api.multi
    @api.depends('categ_id')
    def _compute_blacklisted_category_country_ids(self):
        for product in self:
            flagged_categories = self.env["product.category"].search([
                ("id", "parent_of", product.categ_id.id),
                ("blacklisted_countries_ids", "!=", False)
            ])
            product.blacklisted_category_country_ids = flagged_categories

    @api.multi
    @api.constrains("tmpl_globally_allowed", "tmpl_blacklisted_countries_ids")
    def _constrains_tmpl_globally_allowed(self):
        icp = self.env['ir.config_parameter']
        config = safe_eval(icp.get_param(
            'sale_product_country_filter.blacklist_global_mandatory', 'False'))
        if config and any(
                (template.sale_ok and
                 not template.tmpl_globally_allowed and
                 not template.tmpl_blacklisted_countries_ids)
                for template in self):
            raise ValidationError(
                _("Please check the box 'Globally allowed' if there "
                  "are no blacklisted countries")
            )
