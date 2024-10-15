* To split a sale order line into multiple warehouses you need to click on the tree graph icon in a sale order line. A popup will open, where warehouses and quantities can be selected. Only the warehouses set in the "Alternative Warehouses" field in the warehouse set in the sale order can be selected. Sale order line quantity and its warehouse distributions line quantities are synchronized as follows:
	* When quantity is increased in a sale order line:
		* In case there is a warehouse distribution line related to the warehouse set in the sale order, the increased quantity is added to the quantity in this warehouse fistribution line.
		*  In case there is not a warehouse distribution line related to the warehouse set in the sale order, a new warehouse distribution line related to the warehouse set in the sale order is created containing the increased amount.
	* When quantity is decreased in a sale order line:
		* In case there is a warehouse distribution line related to the warehouse set in the sale order, the decreased quantity is substracted from the quantity amount in this warehouse distribution line. When the amount set in this warehouse distribution line is not enough, the pending amount is randomly substracted from the rest of warehouse distribution lines.
		*  In case there is not a warehouse distribution line related to the warehouse set in the sale order, the decreased quantity is randomly subsctracted from the available warehouse distribution lines.
	* When quantity is modified in a warehouse distribution line, the amount in the sale order line is automatically updated so it matches the total amount in the sale warehouse distribution lines.

* When the multi warehouse options in sale order lines are enabled, changing the general sale order warehouse needs to be done through a wizard, located in the "Other Info" tab, in the "Delivery" section. The button is only visible for users in group "Technical / Manage Multiple Warehouses". 

* A sale order line cannot have multiple warehouse distribution lines related to the same warehouse.

* Once the sale order is validated, the order will be split into multiple pickings, one for each warehouse selected in the warehouse distribution lines.

* **IMPORTANT: In case this module is uninstalled, the warehouse distribution lines will be lost.**
