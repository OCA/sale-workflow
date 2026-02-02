odoo.define("portal_sale_accept_terms.accept_terms", function (require) {
    const publicWidget = require("web.public.widget");

    publicWidget.registry.AcceptTermsWidget = publicWidget.Widget.extend({
        selector: "#modalaccept",
        events: {
            "change #portal_accept_terms": "_onToggleTerms",
            "change .o_portal_signature_form": "_onLoadSignatureForm",
        },

        start: function () {
            this.$acceptTermsCheck = this.$el.find("#portal_accept_terms");
        },

        _onLoadSignatureForm: function () {
            this.$confirm_btn = this.$el.find(".o_portal_sign_submit");
            if (!this.observer) {
                // Observe the disabled attribute of the submit button:
                // when it is enabled also check if terms are accepted
                // if terms are not accepted, keep it disabled
                const $submitButton = this.$el.find(".o_portal_sign_submit");

                const self = this;
                // eslint-disable-next-line no-unused-vars
                const callback = (mutationList, observer) => {
                    for (const mutation of mutationList) {
                        if (mutation.attributeName === "disabled") {
                            const isConfirmEnabled = !mutation.target.disabled;
                            if (isConfirmEnabled) {
                                self._onToggleTerms();
                            }
                        }
                    }
                };

                this.observer = new MutationObserver(callback);

                this.observer.observe($submitButton[0], {attributes: true});
            }
        },

        _onToggleTerms: function () {
            const $acceptTermsCheck = this.$acceptTermsCheck;
            if ($acceptTermsCheck.length) {
                const termsAccepted = $acceptTermsCheck.is(":checked");
                const $confirm_btn = this.$confirm_btn;
                if ($confirm_btn.length) {
                    $confirm_btn.prop("disabled", !termsAccepted);
                }
            }
        },

        destroy: function () {
            if (this.observer) {
                this.observer.disconnect();
            }
            this._super.apply(this, arguments);
        },
    });
});
