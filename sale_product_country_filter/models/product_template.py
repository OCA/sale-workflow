# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import threading

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    tmpl_globally_allowed = fields.Boolean(
        string="Globally allowed",
        help=(
            "If there are no blacklisted countries, you must explicitly set "
            "the product as 'globally allowed'"
        ),
    )
    tmpl_blacklisted_countries_ids = fields.Many2many(
        "res.country", string="Blacklisted countries"
    )

    @api.multi
    @api.constrains("tmpl_globally_allowed", "tmpl_blacklisted_countries_ids")
    def _blacklist_consistency(self):
        test_mode = getattr(threading.currentThread(), 'testing', False)
        testing_current_module = self.env.context.get(
            'testing_sale_product_country_filter')
        if test_mode and not testing_current_module:
            return

        for template in self:
            if (
                    not template.tmpl_globally_allowed and
                    not template.tmpl_blacklisted_countries_ids
            ):
                raise ValidationError(
                    _(
                        "Please check the box 'Globally allowed' if there "
                        "are no blacklisted countries"
                    )
                )
