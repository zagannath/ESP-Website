function renderTree(container) {
    var tree = container.jstree({
        plugins: ["themes", "html_data", "ui"]
    });
    tree.bind("select_node.jstree", function (event, data) {
        $j(".abstract-resource").css("display","none");
        $j(".new-resource-type").css("display","none");
        $j("#view-" + data.args[0].id).css("display","");
        $j("#saved-form").css("display","none");
    });
}

function submitMe () {
    $j.post($j(this).attr('action'), $j(this).serialize(), function(response) {
        //will do something soon
        if (response) {
            alert(response);
        } else {
            $j("#saved-form").css("display","");
        }
    });
    return false;
};
