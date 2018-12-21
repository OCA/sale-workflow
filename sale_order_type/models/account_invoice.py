# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_order_type(self):
        return self.env['sale.order.type'].search([], limit=1)

    sale_type_id = fields.Many2one(
        comodel_name='sale.order.type',
        string='Sale Type', default=_get_order_type)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        sale_type = (self.partner_id.sale_type or
                     self.partner_id.commercial_partner_id.sale_type)
        if sale_type:
            self.sale_type_id = sale_type

    @api.onchange('sale_type_id')
    def onchange_sale_type_id(self):
        if self.sale_type_id.payment_term_id:
            self.payment_term_id = self.sale_type_id.payment_term_id.id
        if self.sale_type_id.journal_id:
            self.journal_id = self.sale_type_id.journal_id.id

    @api.multi
    def match_order_type(self):
        order_types = self.env['sale.order.type'].search([])
        for invoice in self:
            for order_type in order_types:
                if order_type.matches_invoice(invoice):
                    invoice.sale_type_id = order_type
                    invoice.onchange_sale_type_id()
                    break
