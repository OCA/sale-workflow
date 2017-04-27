# -*- encoding: utf-8 -*-
#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author Abdessamad HILALI <abdessamad.hilali@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError



class SaleGenerator(models.Model):
    _name = 'sale.generator'

    name = fields.Char(string='Generator', default='/')
    partner_ids = fields.Many2many(
        comodel_name='res.partner', string="Partner")
    sale_ids = fields.One2many(
        comodel_name='sale.order', inverse_name='generator_id', string="Sales")
    tmpl_sale_id = fields.Many2one(
        comodel_name='sale.order',
        string="Sale Template",
        required=True,
        domain=[('is_template', '=', True)])
    date_order = fields.Datetime(
        string='Date', oldname='date',
        default=fields.datetime.now())
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        required=True,
        string="Warehouse")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generating', 'Generating Order'),
        ('done', 'Done'),
    ], string='State', readonly=True, default='draft')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        related="warehouse_id.company_id",
        store=True)

    @api.multi
    def _prepare_copy_vals(self, partner):
        vals = {}
        vals.update({
            'partner_id': partner.id,
            'generator_id': self.id,
            'warehouse_id': self.warehouse_id.id,
            'company_id': self.warehouse_id.company_id.id,
            'is_template': False,
        })
        return vals

    @api.multi
    def _create_order_for_partner(self, partner):
        self.ensure_one()
        vals = self._prepare_copy_vals(partner)
        self.tmpl_sale_id.copy(default=vals)

    @api.multi
    def button_update_order(self):
        for res in self:
            if not res.partner_ids:
                raise UserError(_(
                    "Can't generate sale order without customer "))
            else:
                res.write({'state': 'generating'})
                res._update_order()

    @api.multi
    def _update_order(self):
        self.ensure_one()
        partner_ids_with_order = [sale.partner_id.id
                                  for sale in self.sale_ids]
        for partner in self.partner_ids:
            if partner.id not in partner_ids_with_order:
                self._create_order_for_partner(partner)
        for sale in self.sale_ids:
            if sale.partner_id not in self.partner_ids:
                sale.unlink()

    @api.multi
    def action_confirm(self):
        for res in self:
            res.write({'state': 'done'})
            for sale in res.sale_ids:
                sale.action_confirm()

    @api.multi
    def write(self, vals):
        res = super(SaleGenerator, self).write(vals)
        if 'partner_ids' in vals and self.state == 'generating':
            self._update_order()
        return res

    def add_generated_partner(self):
        return {'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'name': u"New Customer",
                # ressource associé à l id xml de l'action
                'id': self.env.ref('base.view_partner_form').id,
                # 'id': self.env.ref('sale_generator.action_partner_form').id,
                'view_mode': 'form',
                'target': 'new',
                }

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sale.order.generator') or '/'
        return super(SaleGenerator, self).create(vals)
