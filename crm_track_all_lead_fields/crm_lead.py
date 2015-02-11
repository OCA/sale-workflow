# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp.osv import orm
from openerp.addons.crm.crm_lead import crm_lead

_logger = logging.getLogger(__name__)

IGNORED_FIELDS = (
    'date_action_last',
    'write_date',
)
new_tracked_fields = []
for name, column in crm_lead._columns.items():
    if name in IGNORED_FIELDS:
        continue

    track = getattr(column, "track_visibility", False)
    if track not in ("always", "onchange"):
        new_tracked_fields.append(name)
        column.track_visibility = "onchange"


def track_anything_once(self, cr, uid, obj, ctx):
    if ctx is None:
        # We need the context to track mails being sent. It currently is
        # passed for both write() and create() and should not be None unless
        # someone played in mail thread. Issue a warning and disallow track.
        _logger.warn("Missing context, disallowing track_anything_once")
        return False

    track_ctx = ctx.setdefault("__track_once_context__", {})
    obj_id = obj.get("id", None)
    if obj_id in track_ctx:
        return False
    track_ctx[obj_id] = True
    return True


def merge_track_dict(field, model, new):
    res = {}
    res.update(model._track.get(field, {}))
    res.update(new)
    return res


class CRMLead(orm.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'

    _track = dict(
        (field, merge_track_dict(field, crm_lead, {
            'crm_track_all_lead_fields.mt_field_updated': track_anything_once,
        })) for field in new_tracked_fields
    )
