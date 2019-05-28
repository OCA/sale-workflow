from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)


class crmTeam(models.Model):
    _inherit = 'crm.team'

    member_ids = fields.Many2many('res.users', string='Channel Members')


class resUsers (models.Model):
    _inherit='res.users'
    team_id=fields.Many2many ('crm.team', string = 'Sales Channel',
    help = 'Sales Channel the user is member of. Used to compute the members'
           ' of a sales channel through the inverse one2many')
