from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_invoice_policy(self):
        company = self.env.company
        default_policy = company.default_invoice_policy if hasattr(company, 'default_invoice_policy') else None

        if not default_policy:
            Config = self.env['ir.config_parameter'].sudo()
            default_policy = Config.get_param('sale.default_invoice_policy')

        if not default_policy or default_policy not in ['order', 'delivery']:
            default_policy = 'order'

        _logger.info(f"Default invoice policy from settings: {default_policy}")
        return default_policy

    default_invoice_policy = fields.Selection([
        ('order', 'Ordered quantities'),
        ('delivery', 'Delivered quantities')],
        string='Default Invoicing Policy',
        default=_get_default_invoice_policy,
        help="This will be the default invoicing policy for this partner when creating new sales orders.")

    @api.depends('is_company', 'parent_id')
    def _compute_company_type(self):
        super()._compute_company_type()
        for partner in self:
            if not partner.is_company and partner.default_invoice_policy:
                partner.default_invoice_policy = False

    @api.model
    def set_default_invoice_policy(self):
        default_policy = self._get_default_invoice_policy()
        partners_to_update = self.env['res.partner'].search([
            ('is_company', '=', True),
            '|',
            ('default_invoice_policy', '=', False),
            ('default_invoice_policy', '=', None)
        ])

        if partners_to_update:
            partners_to_update.write({'default_invoice_policy': default_policy})
            _logger.info(f"Updated {len(partners_to_update)} partners with default invoice policy: {default_policy}")
        else:
            _logger.info("No partners found to update")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Update Complete'),
                'message': _('%d partners have been updated with the default invoice policy (%s).') % (len(partners_to_update), default_policy),
                'sticky': False,
                'type': 'success',
            }
        }
