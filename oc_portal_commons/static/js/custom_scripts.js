$(document).ready(function () {
    setSearchParams();
    setHistoryParams();
    setupShowMoreLessControls();
});

function setSearchParams() {
    // toggle advanced search fields
    $("#expand_search").click(function () {
        $(".advanced_search").toggle("slow", function () {
        });
    });
    $(".advanced_search").hide();

    if ($("#id_date_range_0").val() || $("#id_date_range_1").val()
        || $("#id_created_by").val() || $("#id_comment").val()) {
        $(".advanced_search").show();
    }

    // set input fields size
    $('.basic_search input[type="text"]').attr("size", 30);

    // set placeholder for issue/project field
    $('.basic_search input#id_project').attr("placeholder", "CRM Issue/Project code");

    // set proper placeholder for file/version field
    $(".basic_search select.component_type").change(function () {
        var new_value = $(this).val();
        var new_placeholder = "";
        if (new_value == "FILE") {
            new_placeholder = "File in SVN or Nexus artifact";
        } else {
            new_placeholder = "Component version";
        }
        $(".basic_search input.file_or_version").attr("placeholder", new_placeholder);
    });
    $(".basic_search select.component_type").change();

    // set datepicker
    $(".advanced_search #id_date_range_0").add(".advanced_search #id_date_range_1").addClass("datepicker");
    $(".datepicker").datepicker({dateFormat: 'dd-mm-yy'}); // for jquery calendar, yy is YYYY
    $(".datepicker").attr("autocomplete", "off");
    $(".datepicker").attr("placeholder", "dd-mm-yyyy");
}

var dform_params = {
    autoOpen: false,
    title: "Change delivery status",
    height: 400,
    width: 350,
    modal: true,
    buttons: {
        "Submit": {
            id: "submit-dialog",
            text: "Submit",
            click: function () {
                $(this).submit();
                $(this).dialog("close");
            },
        },
        "Cancel": function () {
            $(this).dialog("close");
        },
    },
    open: function () {
        var full_form = $(this).parents(".ui-dialog");
        var submit_btn = full_form.find("#submit-dialog");
        submit_btn.prop("disabled", true);
        var area = $(this).find("textarea");
        var check_text = function () {
            var cur_text = this.value;
            submit_btn.prop("disabled", cur_text == '');
        };
        area.on("input propertychange", check_text);
        area.trigger("propertychange");
    }
};

function setHistoryParams() {
    $(".change-delivery-status").each(function () {
        var btn = $(this);
        var dform = $(this).closest("td.delivery-history").children(".change-status-dialog");
        dform.dialog(dform_params);
        $(this).click(function () {
            dform.dialog("open");
        });
    });

    $(".change-delivery-external-status").each(function () {
        var btn = $(this);
        var status_selector = ".change-status-dialog[status_name='XXX']".replace("XXX", $(this).attr("status_name"));
        var dform = $(this).closest("td.delivery-history").children(".change-status-dialog" + status_selector);
        dform.dialog(dform_params);
        $(this).click(function () {
            dform.dialog("open");
        });
    });

}


function setupShowMoreLessControls() {
    $('input.show_more_less:button').prop("is_expanded", false);
    $('input.show_more_less:button').each(function () {
        updateFilelistVisibility($(this));
    });

    $('input.show_more_less:button').click(function () {
        var node = $(this);
        node.prop("is_expanded", !node.prop("is_expanded"));
        updateFilelistVisibility(node);
    })

}

function updateFilelistVisibility(node) {
    var ALWAYS_SHOWED_ELEMENTS_AMOUNT = 5;
    var delivery_id = node.attr("delivery_id");
    var hint_li = $(`li.more_exists_hint[delivery_id="${delivery_id}"]`);
    var filelist_lis = $(`li.hideable_filelist_element[delivery_id="${delivery_id}"]`);
    var filelist_length = filelist_lis.length;

    if (filelist_length > ALWAYS_SHOWED_ELEMENTS_AMOUNT) {
        var hideable_lis = filelist_lis.slice(ALWAYS_SHOWED_ELEMENTS_AMOUNT, filelist_length);

        var should_expand = node.prop("is_expanded");
        var new_text;
        if (should_expand) {
            hideable_lis.show();
            hint_li.hide();
            new_text = "Show less";
        } else {
            hideable_lis.hide();
            hint_li.show();
            new_text = "Show more";
        }
        node.attr("value", new_text);
    } else {
        hint_li.hide();
        node.hide();
    }


}
