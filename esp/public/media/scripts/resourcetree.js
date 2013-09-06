function createAbstractResource (node) {
    if ($j("#abstract-resource-add").length) {
        alert("Finish creating your previous resource before creating a new one!");
        $j(".jstree").jstree("select_node","#abstract-resource-add",true);
    } else {
        $j(".jstree").jstree("create_node",node,"inside",{
            "data" : {
                "title" : "New Abstract Resource",
                "attr" : {
                    "id" : "abstract-resource-add",
                    "rel" : "abstract-resource",
                }
            },
            "attr" : {
                "rel" : "abstract-resource",
            },
        });
        // set the hidden field for resource_type
        $j("#id_resource_type","#form-abstract-resource-add").attr("value",node.context.id.replace("new-resource-type-",""));
    }
}

function createNewResourceType (node) {
    if ($j("#new-resource-type-add").length) {
        alert("Finish creating your previous resource before creating a new one!");
        $j(".jstree").jstree("select_node","#new-resource-type-add",true);
    } else {
        if (node===null) {
            node = $j(".jstree");
        }
        $j(".jstree").jstree("create_node",node,"inside",{
            "data" : {
                "title" : "New Resource Type", // which, of course, is really a New NewResourceType...
                "attr" : {
                    "id" : "new-resource-type-add",
                    "rel" : "new-resource-type",
                }
            },
            "attr" : {
                "rel" : "new-resource-type",
            },
        });
        if (node) {
            // set the hidden field for parent, iff we have a parent
            $j("#id_parent","#form-new-resource-type-add").attr("value",node.context.id.replace("new-resource-type-",""));
        }
    }
}

function deleteNode (node) {
    if (confirm("Are you sure you want to delete "+$j(".jstree").jstree("get_text",node)+" and all its children?")) {
        var form = $j("#form-"+node.context.id);
        // really, uncheck is_active, submit the form, and remove the node from the rendered tree.
        $j("#id_is_active",form).attr("value","False");
        form.submit();
        $j(".jstree").jstree("delete_node", node);
    }
}


function renderTree(container, editable) {
    var opts = {}
    if (editable) {
        opts.plugins = ["types", "themes", "html_data", "ui", "dnd", "crrm", "contextmenu"];
        opts.crrm = {
            "move" : {
                "check_move" : function (move) {
                    if (move.cr==-1) {
                        //if we're moving to root, we must be a NRT
                        return (move.o.context.id.indexOf("abstract-resource")==-1);
                    } else {
                        //otherwise we can be an AR but must still move under an NRT
                        return (move.cr.context.id.indexOf("abstract-resource")==-1);
                    };
                },
            },
        };
        opts.contextmenu = {
            "items" : function (node) {
                var menu = {};
                menu.del = {
                    "label" : "Delete",
                    "action" : deleteNode,
                };
                menu.createRootNewResourceType = {
                    "label" : "Create Root Resource Type",
                    "action" : function (obj) {
                        createNewResourceType(null);
                    }
                };
                if (node.context.id.indexOf("abstract-resource")==-1) {
                    // only show create options for NRTs
                    menu.createNewResourceType = {
                        "label" : "Create Resource Type",
                        "action" : createNewResourceType,
                    };
                    menu.createAbstractResource = {
                        "label" : "Create Abstract Resource",
                        "action" : createAbstractResource,
                    };
                }
                return menu;
            },
        };
    } else {
        opts.plugins = ["types", "themes", "html_data", "ui"]
    };
    opts.ui = {
        "select_limit" : 1,
    };
    opts.types = {
        "types" : {
            "abstract-resource" : {
                "icon" : { "image" : "/media/images/spacer.gif" },
                "valid_children" : "none",
            },
            "new-resource-type" : {
            },
        },
    };
    opts.themes = {
        "url" : "/media/styles/jquery-ui/jstree/style.css"
    }
    console.log(opts);
    var tree = container.jstree(opts);
    tree.bind("select_node.jstree", function (event, data) {
        nodeA = $j("a",data.rslt.obj) // we want the id from the <a> not the <li>
        $j(".abstract-resource").css("display","none");
        $j(".new-resource-type").css("display","none");
        $j("#view-" + nodeA[0].id).css("display","");
    });
    if (editable) {
        tree.bind("move_node.jstree", function (event, data) {
            var move = data.args[0];
            var childForm = $j("#form-" + move.o.context.id);
            if (move.cr==-1) {
                var parentId = "";
            } else {
                var parentId = move.cr.context.id.replace("new-resource-type-","");
            }
            if (move.o.context.id.indexOf("abstract-resource")==-1) {
                //if we're moving a NRT
                $j("#id_parent", childForm).attr("value",parentId);
            } else {
                //if we're moving an AR
                $j("#id_resource_type", childForm).attr("value",parentId);
            }
            childForm.submit();
            tree.jstree("select_node", move.o, true);
        });
        tree.bind("create_node.jstree", function (event, data) {
            tree.jstree("select_node", data.rslt.obj[0], true);
        });
    }
}

function submitMe () {
    var button = $j(".button",this);
    button.attr("value","Saving...");
    var thisId = $j(this).attr("id");
    var name = $j("#id_name",this).attr("value");
    $j.post($j(this).attr("action"), $j(this).serialize(), function(response) {
        //we'll get the re-rendered form as a response, so replace the form we just submitted with it.  If we changed the name, change it in the tree too.
        var newForm = $j(response);
        $j(thisId.replace("form-","#view-")).replaceWith(newForm);
        $j(".jstree").jstree("rename_node",thisId.replace("form-","#"),name);
        $j(thisId.replace("form-","#")).attr("id",newForm.attr("id").replace("view-",""));
    });
    return false;
};
