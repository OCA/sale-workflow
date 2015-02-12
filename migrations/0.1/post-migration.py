# -*- encoding: utf-8 -*-
##############################################################################
#
#   sale_quick_payment for OpenERP
#   Copyright (C) 2012-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

""" r0.1: Migration 6.1 => 7.0.0.1
    migrate the field payment_id from one2many to payment_ids many2many
"""
__name__ = ("sale.order:: V7 change/rename the field payment_id into a"
            "many2many with the name payment_ids")


def migrate(cr, version):
    if version:
        cr.execute("INSERT INTO account_voucher_sale_order_rel"
                   "(sale_order_id, account_voucher_id) "
                   "(SELECT id, payment_id FROM "
                   " sale_order "
                   "WHERE payment_id IS NOT NULL )")
