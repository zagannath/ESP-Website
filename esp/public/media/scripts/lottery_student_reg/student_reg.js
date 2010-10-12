StudentRegInterface = Ext.extend(Ext.TabPanel, {

    initComponent: function() {
        //this.loadCatalog();
        var config = {
            items: this.makeTabs()
        }
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		StudentRegInterface.superclass.initComponent.apply(this, arguments); 
    },

    loadCatalog: function() {
        /*this.store = new Ext.data.JsonStore({
	        totalProperty: 'total',
	        root: 'data',
            success: true,
            url: 'https://esp.mit.edu/learn/Spark/2010/catalog_json',
            fields: [
                {
                    name: title
                },
                {
                    name: grade_max
                },
                {
                    name: grade_min
                },
                {
                    name: period
                },
                {
                    name: id
                },
            ]
        });*/
    },

/*    makeTimeslotTab: function(timeslot) {
    },

    makeConfirmTab: function() {
    },*/

    makeTabs: function(){
        tabs = [];
        tabs[0]= new Ext.FormPanel({
            id: 'tab1',
            items: [
                        {
                            xtype: 'checkbox',
                            label: 'checkbox1'
                        }
                   ]
        });
        tabs[1]= new Ext.FormPanel({
            id: 'tab2',
            items: [
                    {
                        xtype: 'checkbox',
                        label: 'checkbox2'
                    }
                ]
        });
        /*for(i = 1; i < 20; i++)
        {
            makeTimeslotTab();
        }*/
        return tabs;
    },

/*    confirmRegistration: function() {
    }*/

});

Ext.reg('lottery_student_reg', StudentRegInterface);

stureg = new StudentRegInterface({});

var win = new Ext.Window({
    items: [{ xtype: 'lottery_student_reg'}]
});

onReady = function () {
    win.show();
};
