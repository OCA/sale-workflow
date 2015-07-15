from openerp import fields, models , api


class SaleLineGenerator(models.Model):
        _name='sale.line.generator'

        generator_id = fields.Many2one(
            'sale.generator',
            string="Generator",
            required=True)
        product_id = fields.Many2one(
            'product.product',
            string="Product",
            required=True)
        product_qty= fields.Float(
            'quantity',
            required=True,
            default=1)


class SaleOrder(models.Model):
        _inherit='sale.order'

        generator_id = fields.Many2one('sale.generator', string="Generator")


class SaleGenerator(models.Model):
    _name='sale.generator'

    name = fields.Char('Generator', default='/')
    line_ids = fields.One2many(
        'sale.line.generator',
        'generator_id',
        string="lines")
    partner_ids = fields.Many2many('res.partner', string="Partner")
    sale_ids = fields.One2many('sale.order','generator_id', string="Sales")
    date = fields.Date('Date', default=fields.datetime.now())
    state = fields.Selection([
        ('draft','Draft'),
        ('confirmed','Confirmed'),
        ], 'State', readonly=True, default='draft')

    def _prepare_generator_sale_vals(self, partner):
        return {
            'partner_id': partner.id,
            'generator_id': self.id,
             }

    def _prepare_sale_order_line(self, gline):
         return {
             'product_id': gline.product_id.id,
             'product_uom_qty': gline.product_qty,
         }

    @api.one
    def _create_order_for_partner(self, partner):
        sale_order_obj = self.env['sale.order']
        vals = self._prepare_generator_sale_vals(partner)
        vals['order_line'] = []
        for generator_line in self.line_ids:
            line = self._prepare_sale_order_line(generator_line)
            vals['order_line'].append((0, 0, line))
        sale_order_obj.create(vals)

    @api.one
    def button_confirm(self):
        return self.write({'state': 'confirmed'})

    @api.one
    def _update_order(self):
        sale_order_obj = self.env['sale.order']
        partner_make_order = []
        if self.state == 'confirmed':
            partner_ids_with_order = [sale.partner_id.id
                                      for sale in self.sale_ids]
            for partner in self.partner_ids:
                if partner.id not in partner_ids_with_order:
                    self._create_order_for_partner(partner)
            for sale in self.sale_ids:
                if sale.partner_id not in self.partner_ids:
                    self.unlink()

    @api.multi
    def write(self, vals):
        res = super(SaleGenerator,self).write(vals)
        if 'partner_ids' in vals or 'state' in vals:
            self._update_order()
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('sale.order.generator') or '/'
        return super(SaleGenerator,self).create(vals)
