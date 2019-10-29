# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleGeneralTerm(models.Model):

    _name = 'sale.general.term'
    _description = 'Sale General Term'

    @api.constrains('is_enabled', 'country_ids')
    def _check_is_enabled_country_ids(self):
        for term in self:
            enabled_terms = self.search([
                ('is_enabled', '=', True),
                ('country_ids', 'in', term.country_ids.ids),
                ('lang', '=', term.lang)
            ])
            if len(enabled_terms) > 1:
                raise ValidationError(_(
                    'There are already enabled terms for the Language '
                    'and at least one of the Countries selected. '
                    'Each Country/Language is allowed only one '
                    'enabled General Terms.'
                ))

    @api.constrains('is_enabled', 'active')
    def _check_is_enabled_active(self):
        for term in self:
            if term.is_enabled and not term.active:
                raise ValidationError(_(
                    'Enabled terms must be Active'
                ))

    name = fields.Char(required=True)
    active = fields.Boolean(
        'Active',
        help="Uncheck to archive, making it unavailable for selection.",
        default=True,
    )
    is_enabled = fields.Boolean(
        'Enabled',
        help="Is enabled, will be printed in the Customer Sales Order.",
    )
    country_ids = fields.Many2many(
        'res.country',
        string='Countries')
    lang = fields.Selection(
        lambda self: self.env['res.lang'].get_installed(),
        string='Language')
    terms = fields.Html()

    def get_partner_general_terms(self, partner_id):
        """
        Find the General Terms to use for a particular Partner.
        Looks for the best match based on the Partner's Country and Language.

        :param partner:id: a singleton Partner record
        :returns: the General Terms record if found, False otherwise
        """
        if partner_id:
            partner_id.ensure_one()
            c1 = [('country_ids', 'in', partner_id.country_id.id)]
            c2 = [('lang', '=', partner_id.lang or self.env.user_id.lang)]
            for domain in [c1 + c2, c1, c2]:
                term = self.search([('is_enabled', '=', True)] + domain)
                if term:
                    term.ensure_one()
                    return term
        return False
