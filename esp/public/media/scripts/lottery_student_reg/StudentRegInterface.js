
StudentRegInterface = Ext.extend(Ext.TabPanel, {
   
    initComponent: function () {
	var config = {
	    id: 'sri',
	    width: 1200,
	    autoHeight: true,
	    autoScroll: true,
	    layoutOnTabChange: true,
	    closeable: false,
	    tabWidth: 20,
	    enableTabScroll: true,
	    activeTab: 'instructions',
	    items: [
	        {
		    title: 'Instructions',
		    xtype: 'panel',
		    id: 'instructions',
		    items: [
	                {
			    xtype: 'displayfield',
			    value: 'Welcome To Splash Lottery Registration!'
			},
	                {
			    xtype: 'textarea',
			    value: 'Here are some instructions on how to register for the Splash Lottery',
			    preventScrollbars: true,
			    width: 700
			}
                    ]
		}
            ]
	};
 
	store = this.loadCatalog();
	store.load({});	

	Ext.apply(this, Ext.apply(this.initialConfig, config));
	StudentRegInterface.superclass.initComponent.apply(this, arguments); 
    },

    loadCatalog: function () {
        return new Ext.data.JsonStore({
	        root: '',
		success: true,
	        fields: [
		{
                    name: 'title'
                },
                {
                    name: 'grade_max'
                },
                {
                    name: 'grade_min'
                },
	        {
		    name: 'get_sections'
	        },
		//fields needed for class id generation
		],
		proxy: new Ext.data.HttpProxy({ url: '/learn/Spark/2010/catalog_json' }),
		listeners: {
		    load: {
			scope: this,
			fn: this.makeTabs
		    }
		},		
	    });
    },
    
    makeTabs: function (store, records, options) {
	    tabs = [];
	records.forEach(function(record) {
		r = record.data
		    for (i=0; i< r.get_sections[0].get_meeting_times.length; i++) {
			timeblock = r.get_sections[0].get_meeting_times[i];
			if (!tabs[timeblock.id]){
			    tabs[timeblock.id] = {
				id: timeblock.id,
				xtype: 'form',
				autoScroll: true,
				title: timeblock.short_description,
				items: 
				[{
					xtype: 'field',
					readonly: true,
					fieldLabel: 'First Choice Class',
					id: 'fcc_'+timeblock.id
				}]
			    };
			}
		       
			//one class has a label, a checkbox for 'willing to take' and a radio button for 'flag'
			tabs[timeblock.id].items.push({
				xtype: 'fieldset',
				    layout:  'column',
				    items: [
					    {
						xtype: 'radio',
						name: 'flag', 
						listeners: { //when the radio button is selected change the flag and display title at top
						    check: function(radio, checked) {
							if (checked) {
							    //Ext.getCmp('fcc_'+timeblock.id).setValue(r.title);
							}
						    }
						}
					    },
					    {
						xtype: 'checkbox',
						    name: 'cb_'+r.title
					    },
					    {
						xtype: 'label',
						    text:  r.title
					    }
                                    ], 
			});
		    }
	    }
        );
	    //adds the class tabs
	    j = 0;
	    for (i=0; i < tabs.length; i++){ 
		if(tabs[i]){
		    Ext.getCmp('sri').add(tabs[i]);
		    }
	    }
	    
	    //creates "confirm registration" tab
	    //creates fields for all first choice classes
	    flagged_classes = [];

	    //adds textarea with some explanation
	    flagged_classes.push({
		    xtype: 'displayfield',
		    width: '700',
		    value: 'make sure the first choice classes below are correct, then click "confirm registration"'
	    });

	    for (i=0; i < tabs.length; i++){
		if(tabs[i]){
		    flagged_classes.push({
			    xtype: 'field',
			    fieldLabel: tabs[i].title,
		    });
		}
	    }

	    //adds "confirm registration" button
	    flagged_classes.push({
		    xtype: 'button',
		    text: 'Confirm Registration!',
		    handler: this.confirmRegistration,
	    });

	    //adds above to a form
	    Ext.getCmp('sri').add({
		    xtype: 'form',
		    title: 'Confirm Registration',
		    items: flagged_classes,
	    });

    },

    confirmRegistration: function() {
	    alert('You have just entered the Splash class lottery!');
    }

});

Ext.reg('lottery_student_reg', StudentRegInterface);

var win = new Ext.Window({
	closable: false,
	items: [{ xtype: 'lottery_student_reg', id: 'sri'}],
	});

Ext.onReady(function() {
    win.show();
    });
