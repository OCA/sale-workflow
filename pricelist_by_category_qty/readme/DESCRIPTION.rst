This module will add a button inside the sale order and will compute the discount not by line but by quantities of the same product category, in the same sale order. e.g.: You've defined 10% discount for Category A for 100 PCE min in the List price. 

You try to sell 50 Pieces of Product A and 50 Pieces of Product B (defined on Category A). 
The OnChange in the line will compute the price of the product as usual. 
Then you click on the new button. 
The unit price will be updated as you've sold 50+50 = 100 pieces of the same category! => you will have 10% discount on both lines !

This module was originally developed in v7.0 by the company Julius : https://github.com/julius-network-solutions/julius-openobject-addons/tree/master/pricelist_by_category_qty
