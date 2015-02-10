#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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
from openerp.tests.common import TransactionCase


class TestFinalDestination(TransactionCase):
    def test_no_move_dest_returns_procurement_location(self):
        self.assertEqual('one', self.proc.final_destination().name)

    def test_one_move_returns_move_location(self):
        self.proc.move_dest_id = self.move_two
        self.assertEqual('two', self.proc.final_destination().name)

    def test_two_moves_returns_last_location(self):
        self.proc.move_dest_id = self.move_two
        self.proc.move_dest_id.move_dest_id = self.move_three
        self.assertEqual('three', self.proc.final_destination().name)

    def setUp(self):
        super(TestFinalDestination, self).setUp()
        self.proc = self.env['procurement.order'].new({})
        self.proc.location_id = self.env['stock.location'].new({'name': 'one'})

        self.move_two = self.env['stock.move'].new({})
        self.move_two.location_dest_id = (
            self.env['stock.location'].new({'name': 'two'})
        )

        self.move_three = self.env['stock.move'].new({})
        self.move_three.location_dest_id = (
            self.env['stock.location'].new({'name': 'three'})
        )
