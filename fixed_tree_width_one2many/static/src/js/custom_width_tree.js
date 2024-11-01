odoo.define('fixed_tree_width_one2many.fix_width_list_view', function (require) {
    "use strict";
    
    require("web.EditableListRenderer");
    var ListRenderer = require('web.ListRenderer');
    ListRenderer.include({
        _freezeColumnWidths: function () {
            var res = this._super();


            if (this.state.model=="task.make.purchase.line") {

                this.$el.find('th[data-name="sl_no"]').css({
                    "max-width": "40px",
                    "width": "40px",
                    "min-width": "40px"
                });

                this.$el.find('th[data-name="product_qty"]').css({
                    "max-width": "50px",
                    "width": "50px",
                    "min-width": "50px"
                });
                this.$el.find('th[data-name="purchase"]').css({
                    "max-width": "40px",
                    "width": "40px",
                    "min-width": "40px"
                });



            }

            if (this.state.model=="task.make.delivery.line") {
                this.$el.find('th[data-name="name"]').css({
                    "max-width": "300px",
                    "width": "300px"
                });
                this.$el.find('th[data-name="country_of_origin"]').css({
                    "max-width": "120px",
                    "width": "120px"
                });

                this.$el.find('th[data-name="th_weight"]').css({
                    "max-width": "60px",
                    "width": "60px",

                });

                this.$el.find('th[data-name="product_qty"]').css({
                    "max-width": "50px",
                    "width": "50px",
                    "min-width": "50px"
                });

                this.$el.find('th[data-name="part_number"]').css({
                    "max-width": "100px",
                    "width": "100px"
                });

                 this.$el.find('th[data-name="sl_number"]').css({
                    "max-width": "50px",
                    "width": "50px"
                });
            }
            return res;
        }
    });
});
