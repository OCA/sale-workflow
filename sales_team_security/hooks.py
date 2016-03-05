# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def assign_contacts_team(cr, registry):
    """At installation time, propagate the parent sales team to the children
    contacts that have this field empty, as it's supposed that the intention
    is to have the same.
    """
    cr.execute(
        """
        UPDATE res_partner
        SET section_id=parent.section_id
        FROM res_partner AS parent
        WHERE parent.section_id IS NOT NULL
        AND res_partner.parent_id = parent.id
        AND res_partner.section_id IS NULL
        """)
