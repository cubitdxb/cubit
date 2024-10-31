odoo.define('contact_details_fields.BasicView', function (require) {

"use strict";

  var session = require('web.session');

  var BasicView = require('web.BasicView');

  BasicView.include({

    init: function(viewInfo, params) {

      var self = this;

      this._super.apply(this, arguments);

      var model = self.controllerParams.modelName;

      if(model=='res.partner') {

        session.user_has_group('base.group_system').then(function(has_group) {

          if(!has_group) {

            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;

          }

        });

      }

    },

  });

});
