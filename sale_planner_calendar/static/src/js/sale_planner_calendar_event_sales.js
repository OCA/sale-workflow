odoo.define(
    "sale_planner_calendar.sale_planner_calendar_event_sales",
    function (require) {
        "use strict";
        var ListController = require("web.ListController");
        var ListView = require("web.ListView");

        var KanbanController = require("web.KanbanController");
        var KanbanView = require("web.KanbanView");

        var viewRegistry = require("web.view_registry");

        function renderViewNewSaleOrderButton() {
            if (this.$buttons) {
                var self = this;
                var calendar_summary_id =
                    self.initialState.getContext().default_calendar_summary_id;
                this._rpc({
                    model: "sale.planner.calendar.event",
                    method: "action_open_sale_order",
                    args: [false, {new_order: true}],
                    context: {calendar_summary_id: calendar_summary_id || false},
                }).then(function (action) {
                    self.$buttons.on("click", ".o_button_new_sale_order", function () {
                        self.do_action(action);
                    });
                });
            }
        }

        var SalePlannerCalendarEventListController = ListController.extend({
            willStart: function () {
                var self = this;
                var ready = this.getSession()
                    .user_has_group("sales_team.group_sale_salesman")
                    .then(function (is_sale_user) {
                        if (is_sale_user) {
                            self.buttons_template =
                                "SalePlannerCalendarEventListView.buttons";
                        }
                    });
                return Promise.all([this._super.apply(this, arguments), ready]);
            },
            renderButtons: function () {
                this._super.apply(this, arguments);
                renderViewNewSaleOrderButton.apply(this, arguments);
            },
        });

        var SalePlannerCalendarEventListView = ListView.extend({
            config: _.extend({}, ListView.prototype.config, {
                Controller: SalePlannerCalendarEventListController,
            }),
        });

        var SalePlannerCalendarEventKanbanController = KanbanController.extend({
            willStart: function () {
                var self = this;
                var ready = this.getSession()
                    .user_has_group("sales_team.group_sale_salesman")
                    .then(function (is_sale_user) {
                        if (is_sale_user) {
                            self.buttons_template =
                                "SalePlannerCalendarEventKanbanView.buttons";
                        }
                    });
                return Promise.all([this._super.apply(this, arguments), ready]);
            },
            renderButtons: function () {
                this._super.apply(this, arguments);
                renderViewNewSaleOrderButton.apply(this, arguments);
            },
        });

        var SalePlannerCalendarEventKanbanView = KanbanView.extend({
            config: _.extend({}, KanbanView.prototype.config, {
                Controller: SalePlannerCalendarEventKanbanController,
            }),
        });

        viewRegistry.add(
            "sale_planner_calendar_event_tree",
            SalePlannerCalendarEventListView
        );
        viewRegistry.add(
            "sale_planner_calendar_event_kanban",
            SalePlannerCalendarEventKanbanView
        );
    }
);
