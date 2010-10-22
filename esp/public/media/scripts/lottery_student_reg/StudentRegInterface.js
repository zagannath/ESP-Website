
StudentRegInterface = Ext.extend(Ext.TabPanel, {

    //names of the timeblocks in the django database.  configure per program.
    //this is necessary so they can be in order
    tab_names:  [
		     'First class period: Sat 9:05 - 9:55 AM', 
		     'Second class period: 10:05 - 10:55 AM', 
		     'Third class period: 11:05 - 11:55 AM', 
		     'Fourth class period: 12:05 - 12:55 PM\r\n\r\nLunch A will run during this hour.', 
		     'Fifth class period: 1:05 - 1:55 PM\r\n\r\nLunch B will run during this hour.', 
		     'Sixth class period: 2:05 - 2:55', 
		     'Seventh class period: 3:05 - 3:55 PM', 
		     'Eighth class period: 4:05 - 4:55 PM', 
		     'Ninth class period: 5:05 - 5:55 PM', 
		     'Tenth class period: 7:05 - 7:55 PM', 
		     'Eleventh class period: 8:05 - 8:55 PM', 
		     'Twelfth class period: 9:05 - 9:55 PM'
		     ],
         

    initComponent: function () {
	num_tabs = this.tab_names.length;

	var config = {
	    id: 'sri',
	    width: 1200,
	    autoHeight: true,
	    autoScroll: true,
	    deferredRender: false,
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
	    //make a tab for each class period
	    //num_tabs and tab_names need to be modified for a particular program
	tabs = [];

	//makes tabs with id = short_description of timeblock
	    for(i = 0; i < num_tabs; i++)
	    {
		{
		    tabs[this.tab_names[i]] = 
		    {
			xtype: 'form',
			id: this.tab_names[i],
			title: this.tab_names[i],
			items: 
			[
		            {
				xtype: 'field',
				id: 'flag' + this.tab_names[i],
				fieldLabel: 'Flagged Class'
			    } 
                        ]
		    }
		}
	    }

	    for (i = 0; i < records.length; i++)
	    { 
		r = records[i].data;
		num_sections = r.get_sections.length;
		for (j = 0; j < num_sections; j ++)
		{
		    if(r.get_sections[j].get_meeting_times.length >0)
		    {
			timeblock = r.get_sections[j].get_meeting_times[0]
			tabs[timeblock.short_description].items.push({
				    xtype: 'fieldset',
				    layout: 'column',
				    name: timeblock.short_description+r.title,
				    items: 
				    [
			               {
					   xtype: 'radio',
					   name: 'flag'+timeblock.short_description,
					   listeners: { //listener changes the flagged classes box at the top when the flagged class changes
					       check: function (radio, checked) {
						   if(checked)
						   {
						       //Ext.getCmp('flag'+timeblock.short_description).setValue(r.title);
						       //Ext.getCmp('confirm_flag'+timeblock.short_description).setValue(r.title);
						       
						       //for (i in Ext.getCmp('flag'+timeblock.short_description)) { alert(i); }

						       //Ext.getCmp('flag'+timeblock.short_description).getEl().repaint();
						       //Ext.getCmp('confirm_flag'+timeblock.short_description).getEl().repaint(); 
						   }
					       }
					   }
				       }, 
			               {
					   xtype: 'checkbox',
					   name: 'checkbox_'+r.id
				       }, 
			               { 
					   xtype: 'displayfield',
					   value: r.title
				       }
				    ]
			
			});
		    }
		}
	    }
	
	    //adds tabs to tabpanel
	    for (i = 0; i < num_tabs; i ++)
	    {
		Ext.getCmp('sri').add(tabs[this.tab_names[i]]);
	    }

	    //creates "confirm registration" tab
	    //creates fields for all first choice classes
	    flagged_classes = [];

	    //adds textarea with some explanation
	    flagged_classes.push({
		    xtype: 'displayfield',
		    width: '700',
		    value: 'Please make sure the flagged classes below are correct, then click "confirm registration"'
	    });

	    flagged_classes.push({
		    xtype: 'displayfield',
		    width: '700',
		    value: 'Flagged Classes'
	    });

	    for (i=0; i < num_tabs; i++){
		if(tabs[this.tab_names[i]]){
		    flagged_classes.push({
			    xtype: 'field',
			    id: 'confirm_flag'+this.tab_names[i], 
			    fieldLabel: this.tab_names[i],
		    });
		}
	    }

	    //adds "confirm registration" button
	    flagged_classes.push({
		    xtype: 'button',
		    text: 'Confirm Registration!',
		    handler: this.confirmRegistration
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
	    tabpanel = Ext.getCmp('sri');
	    for(i = 0; i < tabpanel.tab_names.length; i++){
		Ext.getCmp(tabpanel.tab_names[i]).getForm().submit({ url: 'lsr_submit' });
	    }
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
