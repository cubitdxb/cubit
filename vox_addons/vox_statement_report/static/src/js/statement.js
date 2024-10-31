odoo.define('vox_statement_report.StatementFollowupFormController', function (require) {
"use strict";

var FormController = require('web.FormController');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


var core = require('web.core');
var ListController = require('web.ListController');
var rpc = require('web.rpc');
var session = require('web.session');
var _t = core._t;
    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
              this.$buttons.find('.o_account_statement_report_button').click(this.proxy('action_def')) ;            }
        },
        action_def: function () {
            var self =this
            var user = session.uid;
            var file = false
            self.do_action({
                        name: _t('Warning Receive Invoices'),
                        type: 'ir.actions.act_window',
                        res_model: 'statement.account.report.wizard',
                        views: [[false, 'form']],
                        view_mode: 'form',
                        target: 'new',
                    })
                    }
    });

//var StatementFollowupFormController = FormController.extend({
//    events: _.extend({}, FormController.prototype.events, {
//        'click .o_account_statement_report_button': '_onstatementReport',
//    }),
//
//    /**
//     * @override
//     */
//    init: function () {
//        this._super.apply(this, arguments);
//        // force refresh search view on subsequent navigation
//        delete this.searchView;
//        this.hasActionMenus = false;
//    },
//
//    //--------------------------------------------------------------------------
//    // Public
//    //--------------------------------------------------------------------------
//    /**
//     * @override
//     */
//    renderButtons: function ($node) {
//        this.$buttons = $(QWeb.render("CustomerStatements.buttons", {
//            widget: this
//        }));
//        if ($node) {
//            this.$buttons.appendTo($node);
//        }
//    },
//    /**
//     * Update the buttons according to followup_level.
//     *
//     * @override
//     */
//    updateButtons: function () {
//        let setButtonClass = (button, primary) => {
//            /* Set class 'btn-primary' if parameter `primary` is true
//             * 'btn-secondary' otherwise
//             */
//            let addedClass = primary ? 'btn-primary' : 'btn-secondary'
//            let removedClass = !primary ? 'btn-secondary' : 'btn-primary'
//            this.$buttons.find(`button.${button}`)
//                .removeClass(removedClass).addClass(addedClass);
//        }
//        if (!this.$buttons) {
//            return;
//        }
//        var followupLevel = this.model.localData[this.handle].data.followup_level;
//        setButtonClass('o_account_followup_print_letter_button', followupLevel.print_letter)
//        setButtonClass('o_account_followup_send_mail_button', followupLevel.send_email)
//        setButtonClass('o_account_followup_send_sms_button', followupLevel.send_sms)
//        const $buttonFollowupManualAction = this.$buttons.find('button.o_account_followup_manual_action_button');
//        if (followupLevel.manual_action) {
//            $buttonFollowupManualAction.text(followupLevel.manual_action_note);
//            $buttonFollowupManualAction.show()
//            setButtonClass('o_account_followup_manual_action_button', !followupLevel.manual_action_done)
//        } else {
//            $buttonFollowupManualAction.hide();
//        }
//    },
//
//
//
//    _displayDone: function () {
//        this.$buttons.find('button.o_account_followup_done_button').show();
//        this.renderer.removeMailAlert();
//    },
//
//    _getPartner() {
//        return this.model.get(this.handle, {raw: true}).res_id;
//    },
//
//
//    _renderSearchView: function () {
//        var progressInfo = this.model.getProgressInfos();
//        var total = progressInfo.numberDone + progressInfo.numberTodo;
//        this.$searchview = $(QWeb.render("CustomerStatements.followupProgressbar", {
//            current: progressInfo.numberDone,
//            max: progressInfo.numberDone + progressInfo.numberTodo,
//            percent: (progressInfo.numberDone / total * 100),
//        }));
//    },
//    /**
//     * Update the pager with the progress of the follow-ups.
//     *
//     * @private
//     * @override
//     */
//    _updatePaging: function () {
//        const { currentElementIndex, numberTodo } = this.model.getProgressInfos();
//        const state = this.model.get();
//        return this._super(state, {
//            currentMinimum: currentElementIndex + 1,
//            size: numberTodo,
//        });
//    },
//    /**
//     * Replace the search view with a progress bar.
//     *
//     * @override
//     */
//    _updateControlPanelProps: function () {
//        this._super.apply(this, arguments);
//        this._renderSearchView();
//        this.controlPanelProps.cp_content.$searchview = this.$searchview;
//    },
//
//     async _onstatementReport() {
//        this.model.doSendSMS(this.handle);
//        this.options = {
//            partner_id: this._getPartner()
//        };
//        let action = await this._rpc({
//            model: 'account.followup.report',
//            method: 'print_followups',
//            args: [this.options],
//        })
//        this.do_action(action, {
//            on_close: (infos) => {
//                if (!infos) {
//                    this._removeHighlightSMS()
//                    this._displayDone();
//                    this.renderer.renderSMSAlert();
//                }
//            },
//        })
//    },
//
//});
//return StatementFollowupFormController;
});
