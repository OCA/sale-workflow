from openerp import fields, models, api


class SaleOrder(models.Model):
        _inherit = 'sale.order'

        generator_id = fields.Many2one('sale.generator', string="Generator")
        is_template = fields.Boolean()


class SaleGenerator(models.Model):
    _name = 'sale.generator'

    name = fields.Char('Generator', default='/')
    partner_ids = fields.Many2many('res.partner', string="Partner")
    sale_ids = fields.One2many('sale.order', 'generator_id', string="Sales")
    tmpl_sale_id = fields.Many2one(
        'sale.order',
        string="Sale Template",
        required=True,
        domain=[('is_template', '=', True)])
    date = fields.Date(
        'Date',
        default=fields.datetime.now())
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        required=True,
        string="Warehouse")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generating', 'Generating Order'),
        ('done', 'Done'),
        ], 'State', readonly=True, default='draft')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        related="warehouse_id.company_id",
        store=True)

    @api.multi
    def _prepare_copy_vals(self, partner):
        vals = self.env['sale.order'].onchange_partner_id(partner.id)['value']
        vals.update({
            'partner_id': partner.id,
            'generator_id': self.id,
            'warehouse_id': self.warehouse_id.id,
            'company_id': self.warehouse_id.company_id.id,
            'is_template': False,
            })
        return vals

    @api.one
    def _create_order_for_partner(self, partner):
        vals = self._prepare_copy_vals(partner)
        self.tmpl_sale_id.copy(default=vals)

    @api.one
    def button_confirm(self):
        self.write({'state': 'generating'})
        self._update_order()

    @api.one
    def _update_order(self):
        partner_ids_with_order = [sale.partner_id.id
                                  for sale in self.sale_ids]
        for partner in self.partner_ids:
            if partner.id not in partner_ids_with_order:
                self._create_order_for_partner(partner)
        for sale in self.sale_ids:
            if sale.partner_id not in self.partner_ids:
                sale.unlink()

    @api.one
    def action_button_confirm(self):
        self.write({'state': 'done'})
        for sale in self.sale_ids:
            sale.action_button_confirm()

    @api.multi
    def write(self, vals):
        res = super(SaleGenerator, self).write(vals)
        if 'partner_ids' in vals and self.state == 'generating':
            self._update_order()
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('sale.order.generator') or '/'
        return super(SaleGenerator, self).create(vals)
