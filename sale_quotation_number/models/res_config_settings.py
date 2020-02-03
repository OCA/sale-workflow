# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# Richard deMeester <richard.demeester@willdooit.com> (Willdoo IT)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    keep_name_so = fields.Boolean(
        related='company_id.keep_name_so',
        readonly=False)
