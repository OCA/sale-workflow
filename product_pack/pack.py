# -*- encoding: latin-1 -*-


import math
from openerp.osv import fields,osv

class product_pack( osv.osv ):
    _name = 'product.pack.line'
    _rec_name = 'product_id'
    _columns = {
        'parent_product_id': fields.many2one( 'product.product', 'Parent Product', ondelete='cascade', required=True ),
        'quantity': fields.float( 'Quantity', required=True ),
        'product_id': fields.many2one( 'product.product', 'Product', required=True ),
    }

product_pack()

class product_product( osv.osv ):
    _inherit = 'product.product'
    _columns = {
        'stock_depends': fields.boolean( 'Stock depends of components', help='Mark if pack stock is calcualted from component stock' ),
        'pack_fixed_price': fields.boolean( 'Pack has fixed price', help='Mark this field if the public price of the pack should be fixed. Do not mark it if the price should be calculated from the sum of the prices of the products in the pack.' ),
        'pack_line_ids': fields.one2many( 'product.pack.line','parent_product_id', 'Pack Products', help='List of products that are part of this pack.' ),
    }

    def get_product_available( self, cr, uid, ids, context=None ):
        """ Calulate stock for packs, return  maximum stock that lets complete pack """
        result={}
        # for product in self.browse( cr, uid, ids, context=context ):
        result = super( product_product, self ).get_product_available( cr, uid, ids, context=context )
        if not isinstance(ids, list):
            ids = [ids]
        stock_depends_products = self.search(cr, uid, [('stock_depends', '=',True),('id','in',ids)], context=context) 
        for product in self.browse( cr, uid, stock_depends_products, context=context ):

            first_subproduct = True
            pack_stock = 0
            # Check if the pack has subproducts
            if product.pack_line_ids:
                # Take the stock/virtual stock of all subproducts
                subproducts_stock = super( product_product, self ).get_product_available(cr, uid, [ line.product_id.id for line in product.pack_line_ids ], context=context )

                # Go over all subproducts, take quantity needed for the pack and its available stock
                for subproduct in product.pack_line_ids:
                    if first_subproduct:
                        subproduct_quantity = subproduct.quantity
                        subproduct_stock = subproducts_stock[ subproduct.product_id.id ]
                        # Calculate real stock for current pack from the subproduct stock and needed quantity
                        pack_stock = math.floor( subproduct_stock / subproduct_quantity )
                        first_subproduct = False
                        continue
                    # Take the info of the next subproduct
                    subproduct_quantity_next = subproduct.quantity
                    subproduct_stock_next = subproducts_stock[ subproduct.product_id.id ]
                    pack_stock_next = math.floor( subproduct_stock_next / subproduct_quantity_next )
                    # compare the stock of a subproduct and the next subproduct
                    if pack_stock_next < pack_stock:
                        pack_stock = pack_stock_next
                # result is the minimum stock of all subproducts
                result[ product.id ] = pack_stock
            else:
                stock = super( product_product, self ).get_product_available( cr, uid, [ product.id ], context=context )
                result[ product.id ] = stock[ product.id ]
        return result

# back up de funcion
    # def get_product_available( self, cr, uid, ids, context=None ):
    #     """ Calulate stock for packs, return  maximum stock that lets complete pack """
    #     result={}
    #     for product in self.browse( cr, uid, ids, context=context ):
    #         stock = super( product_product, self ).get_product_available( cr, uid, [ product.id ], context=context )
    #         print product.id
    #         # Check if product stock depends on it's subproducts stock.
    #         if not product.stock_depends:
    #             result[ product.id ] = stock[ product.id ]
    #             continue

    #         first_subproduct = True
    #         pack_stock = 0

    #         # Check if the pack has subproducts
    #         if product.pack_line_ids:
    #             # Take the stock/virtual stock of all subproducts
    #             subproducts_stock = self.get_product_available( cr, uid, [ line.product_id.id for line in product.pack_line_ids ], context=context )
    #             # Go over all subproducts, take quantity needed for the pack and its available stock
    #             for subproduct in product.pack_line_ids:
    #                 if first_subproduct:
    #                     subproduct_quantity = subproduct.quantity
    #                     subproduct_stock = subproducts_stock[ subproduct.product_id.id ]
    #                     # Calculate real stock for current pack from the subproduct stock and needed quantity
    #                     pack_stock = math.floor( subproduct_stock / subproduct_quantity )
    #                     first_subproduct = False
    #                     continue
    #                 # Take the info of the next subproduct
    #                 subproduct_quantity_next = subproduct.quantity
    #                 subproduct_stock_next = subproducts_stock[ subproduct.product_id.id ]
    #                 pack_stock_next = math.floor( subproduct_stock_next / subproduct_quantity_next )
    #                 # compare the stock of a subproduct and the next subproduct
    #                 if pack_stock_next < pack_stock:
    #                     pack_stock = pack_stock_next
    #             # result is the minimum stock of all subproducts
    #             result[ product.id ] = pack_stock
    #         else:
    #             result[ product.id ] = stock[ product.id ]
    #     return result

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
