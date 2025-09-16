# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

import pytz

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartnerIdNumber(models.Model):
    _inherit = "res.partner.id_number"

    @api.model
    def message_error_identifications(
        self, product_tmpl_ids, diff_identification_ids, required=False
    ):
        """
        Define a message identifications by product

        :param product_tmpl_ids: Products that have at least one identification
                                 category defined.
        :param diff_identification_ids: Required or optional identifications.
        :param required: Defines whether what is being validated is required or not.
        :return: A message with the identification categories per product.
        """
        message = ""
        for product in product_tmpl_ids:
            identifications = product.mapped("product_tmpl_category_ids").filtered(
                lambda x: x.is_mandatory == required
                and x.category_id.id in diff_identification_ids
            )
            if identifications:
                message += _("\n%(product)s\n%(categories)s") % {
                    "product": product.name,
                    "categories": "\n".join(
                        identifications.mapped(
                            lambda x: f"\u2003\u2022\u2009"
                            f"{x.category_id.name}\u2009"
                            f"{f'({x.message})' if x.message else ''}"
                        )
                    ),
                }
        return message

    def _identification_domain(self, **params):
        """
        Build a domain to filter valid identifications
        :param params: Dictionary of expected parameters
        :return: list: List of tuples representing the search domain
        """
        user_tz = self.env.user.tz or self.env.context.get("tz")
        user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
        now_dt = datetime.now().astimezone(user_pytz).date()
        if not params.get("partner_id", False):
            return []
        return [
            ("partner_id", "=", params.get("partner_id")),
            "|",
            "|",
            "|",
            "&",
            ("valid_from", "=", False),
            ("valid_until", "=", False),
            "&",
            "&",
            ("valid_from", "!=", False),
            ("valid_until", "=", False),
            ("valid_from", "<=", now_dt),
            "&",
            "&",
            "&",
            ("valid_from", "!=", False),
            ("valid_until", "!=", False),
            ("valid_from", "<=", now_dt),
            ("valid_until", ">=", now_dt),
            "&",
            "&",
            ("valid_from", "=", False),
            ("valid_until", "!=", False),
            ("valid_until", ">=", now_dt),
        ]

    @api.model
    def validate_identification(self, **params):
        """
        Allows you to obtain the difference between 2 recordset IDs

        :param params: A dictionary of values where at least
                       the value 'compare_identification_ids' and 'partner_id'
                       must be present to validate the identifications
        :return: A set of records with the difference between submitted
                identifications and those of the partner
        """
        identification_ids = params.get("compare_identification_ids", set())
        partner_id = params.get("partner_id", False)
        if not partner_id:
            raise ValidationError(_("A client is required to verify identifications."))
        domain = self._identification_domain(**{"partner_id": partner_id})
        partner_identification_ids = self.env["res.partner.id_category"]
        for id_number in self.env["res.partner.id_number"].search(domain):
            id_number.category_id.validate_id_number(id_number)
            partner_identification_ids |= id_number.category_id
        return (
            identification_ids - partner_identification_ids
            if identification_ids
            else partner_identification_ids
        )
