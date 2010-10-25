checkbox_ids = [];
flag_ids = [];

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
	    deferredRender: true,
	    forceLayout: true,
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
			    value: '<p>Welcome To Splash Lottery Registration!<\p>'
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
 
	this.loadCatalog();
	this.store.load({});	

	Ext.apply(this, Ext.apply(this.initialConfig, config));
	StudentRegInterface.superclass.initComponent.apply(this, arguments); 
    },

    loadCatalog: function () {
	    this.store =  new Ext.data.JsonStore({
		id: 'store',
	        root: '',
		success: true,
	        fields: [
	        {
		    name: 'id'
		},  
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
		tabs[this.tab_names[i]] = 
		    {
			xtype: 'form',
			id: this.tab_names[i],
			title: this.tab_names[i],
			items: 
			[
			    /*{
		                xtype: 'field',
				id: flag_id+ '_field',
				fieldLabel: 'Flagged Class'
			    }*/
                        ]
		    }
	    }
	    //itterate through records (classes)
	    for (i = 0; i < records.length; i++)
	    { 
		r = records[i];
		num_sections = r.data.get_sections.length;
		//itterate through times a class is offered
		for (j = 0; j < num_sections; j ++)
		{
		    if(r.data.get_sections[j].get_meeting_times.length >0)
		    {
			timeblock = r.data.get_sections[j].get_meeting_times[0];
		
			//puts id of checkbox in the master list
			checkbox_id = r.data.id + '_' + timeblock.id;
			checkbox_ids.push(checkbox_id);
		
			flag_id = 'flag_'+timeblock.id;
			if(flag_ids.indexOf(flag_id)==-1){
			    flag_ids.push(flag_id);
			}

			tabs[timeblock.short_description].items.push({
				    xtype: 'fieldset',
				    layout: 'column',
				    id: timeblock.short_description+r.data.title,
				    name: timeblock.short_description+r.data.title,
				    items: 
				    [
			               {
					   xtype: 'radio',
					   id: 'flag_'+checkbox_id,
					   name: flag_id,
					   inputValue: r.data.id,
					   listeners: { //listener changes the flagged classes box at the top when the flagged class changes
					       
					   }
				       }, 
			               {
					   xtype: 'checkbox',
					   name: checkbox_id,
					   id: checkbox_id
				       }, 
			               { 
					   xtype: 'displayfield',
					   value: r.data.title,
					   id: 'title_'+ checkbox_id 
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

	/*
	     for (i=0; i < num_tabs; i++){
		 if(tabs[this.tab_names[i]]){
		     flagged_classes.push({
			     xtype: 'field',
			     id: 'confirm_flag'+this.tab_names[i], 
			     fieldLabel: this.tab_names[i],
		     });
		 }
		 }*/

	     //adds "confirm registration" button
	     flagged_classes.push({
		     xtype: 'button',
		     text: 'Confirm Registration!',
		     handler: this.promptCheck,
	     });

	     //adds above to a form
	     Ext.getCmp('sri').add({
		     xtype: 'form',
		     title: 'Confirm Registration',
		     items: flagged_classes,
		     });
     },

    promptCheck: function() {
	    flagged_classes = 'Please check to see that these are the classes you intended to flag:<ul>';
	    for(i = 0; i<checkbox_ids.length; i++){
		if (Ext.getCmp('flag_'+checkbox_ids[i]).getValue() == true){
		    title = Ext.getCmp('title_'+checkbox_ids[i]).getValue();
		    flagged_classes = flagged_classes + title + '<ul>';
		}
	    }
	    Ext.Msg.show({
		    title:  'Flagged Classes',
		    msg: flagged_classes,
		    buttons: {ok:'These look good.  Enter me into the Splash lottery!', cancel:'Wait!  No!  Let me go back and edit them!'},
		    fn: function(button) {
			if (button == 'ok'){Ext.getCmp('sri').confirmRegistration();}
			if (button == 'cancel'){Ext.Msg.hide();}
		    }
		});
    },

     confirmRegistration: function() {
	     tabpanel = Ext.getCmp('sri');
	    //submitForm.getForm().submit({url: 'lsr_submit'})
	     classes = new Object;
	     count = 0;

	     for(i=0; i<checkbox_ids.length; i++) {
		 checkbox = Ext.getCmp(checkbox_ids[i]);
		 classes[checkbox_ids[i]] = checkbox.getValue();
		 flag_id = 'flag_'+checkbox_ids[i];
		 flag = Ext.getCmp(flag_id);
		 classes[flag_id] = flag.getValue();
	     }

	     /*
	     for(i=0; i<flag_ids.length; i++){
	         flag = Ext.getCmp(flag_ids[i]);
		 classes[flag_ids[i]] = flag.getValue();
		 }*/

	     data = Ext.encode(classes);
	     Ext.Ajax.request({
		     url: 'lsr_submit',
		     params: data,
		     method: 'POST'
		 });
    }
});

Ext.reg('lottery_student_reg', StudentRegInterface);


var win = new Ext.Window({
	closable: false,
	items: [{ xtype: 'lottery_student_reg', id: 'sri'},
		//submitForm
        ],
});

Ext.onReady(function() {
    win.show();
    //submitForm.getForm().submit({url: 'lsr_submit'});
});
