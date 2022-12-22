odoo.define('odoo_create_portal_po_request.add_po_line', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.AddVendorRfq = publicWidget.Widget.extend({

    selector: '.prsit_parent',
    events: {
        'click #addPoLine': '_onAddLine',
        'change .prsit_product_select': '_onChangeProduct',
        'click .js_delete_product': '_onClickRemoveLine',
    },
    start: function () {
        var def = this._super.apply(this, arguments);
        this.line_seq = 2;
        return def;
    },
    _onAddLine: function () {
        var tr_value = $(".prsit_tr").clone()[0];
        $(tr_value).find("select").val('');
        $(tr_value).find("input.prsit_product_qty").val(1);
        $(tr_value).find("textarea").text('');

        $(tr_value).find("select.prsit_product_select").attr("name", `product_id_${this.line_seq}`);
        $(tr_value).find("select.prsit_product_select").attr("required", "required");

        $(tr_value).find("textarea.prsit_product_desc").attr("name", `description_${this.line_seq}`);
        $(tr_value).find("textarea.prsit_product_desc").attr("required", "required");

        $(tr_value).find("input.prsit_product_qty").attr("name", `quantity_${this.line_seq}`);
        $(tr_value).find("input.prsit_product_qty").attr("required", "required");

        $(tr_value).removeClass('o_hidden')
        $(".prsit_table").append(tr_value);
        $(".sequence").val(this.line_seq);
        this.line_seq += 1;
    },
    _onChangeProduct: function(ev){
        $(ev.currentTarget).parents("tr").find("textarea.prsit_product_desc").text($(ev.currentTarget).find("option:selected").attr("desc"));
        $(ev.currentTarget).parents("tr").find("textarea.prsit_product_desc").attr("value", $(ev.currentTarget).find("option:selected").attr("desc"));
    },
    _onClickRemoveLine: function(ev){
        $(ev.currentTarget).parents("tr").remove()
    },

});

return publicWidget.registry.AddVendorRfq;

});
