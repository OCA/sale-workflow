# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
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
#


def check_state_and_exceptions(sale_order, state, exc_id):
    assert sale_order.state == state, (
        "Incorrect state %s instead of %s" % (sale_order.state, state))
    assert exc_id in [x.id for x in sale_order.exception_ids],\
        "No exception for %s" % sale_order.name

    assert not [x for x in sale_order.exception_ids if x.id != exc_id],\
        "Wrong sale exception detected for %s" % sale_order.name
