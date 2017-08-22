# coding: utf-8
# © 2017 David BEAL & Alexis DE LATTRE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleCovenant(models.Model):
    _name = "sale.covenant"
    _description = "Sale Covenant (commitment, engagement, pledge)"

    name = fields.Char(required=True)
    code = fields.Char(string='Number', copy=False, size=50)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer', ondelete='restrict',
        required=True,
        domain=[('customer', '=', True), ('parent_id', '=', False)])
    image = fields.Binary(
        string="Image",
        help="Covenant image represents market or commitment")
    active = fields.Boolean(
        default=True,
        help="The active field allows you to make your record "
             "without effect but without remove it.")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', index=1,
        default=lambda self: self.env['res.company']._company_default_get())
    comment = fields.Text(string='Comment')
    sale_ids = fields.One2many(
        comodel_name='sale.order', inverse_name='covenant_id',
        string='Sales', readonly=True,
        domain=[('state', 'not in', ('draft', 'sent', 'cancel'))])

    @api.multi
    @api.depends('code', 'name')
    def compute_display_name_field(self):
        for covenant in self:
            covenant.display_name = u'[%s] %s' % (covenant.code, covenant.name)

    _sql_constraints = [(
        'code_partner_company_unique',
        'unique(code, partner_id, company_id)',
        'This covenant number already exists for this customer!'
    )]
