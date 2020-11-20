


'''
summary: notify decision for check window
input: dict_notify = {'broadcast' : 0,
                   'notification-channels' : 0,
                   'lifecycle-start' : 0,
                   'lifecycle-resume' : 0,
                   'lifecycle-create' : 0
                  }
output: 0
'''
def check_notify(dict_notify):
    is_notify = 0
    
    is_notify += dict_notify['broadcast']
    is_notify += dict_notify['notification-channels']
    is_notify += dict_notify['lifecycle-start']
    is_notify += dict_notify['lifecycle-resume']
    is_notify += dict_notify['lifecycle-create']
    
    return is_notify


'''
summary: check goodevents at window
input: eventName = broadcast
        df =                     %eventName  \
            eventTimestamp                                                           
            2020-10-29 19:17:09  broadcast   
            2020-10-29 19:22:52  broadcast   

                               eventParams  \
            eventTimestamp                                                           
            2020-10-29 19:17:09        {"action": "android.net.wifi.STATE_CHANGE"}   
            2020-10-29 19:22:52  {"action": "android.net.wifi.STATE_CHANGE", "n...   

                                 is_notify  
            eventTimestamp                  
            2020-10-29 19:17:09          0  
            2020-10-29 19:22:52          0  

output: 0
'''
def goodevents(df , eventName):
    is_goodevent = 0
    
    dict_all_goodevents = {'broadcast' : {'action':['android.intent.action.DREAMING_STOPPED' 
                                                    , 'android.intent.action.HEADSET_PLUG' , 'android.intent.action.SCREEN_ON'
                                                   ,'android.net.conn.CONNECTIVITY_CHANGE','android.net.wifi.STATE_CHANGE'
                                                   ]
                                         },
                           'notification-channels' : {'importance': [4 , 3]
                                                     },
                           'lifecycle-start' : {'any':['any']
                                               },
                           'lifecycle-resume' : {'any':['any']
                                               },
                           'lifecycle-create' : {'any':['any']
                                               }
                      
                      }
    check_goodevents = dict_all_goodevents[eventName]
    
    try:
        df = df['eventParams'].apply(lambda x: json.loads(x.replace("'", "\"")))
        df = pd.DataFrame(list(df))
        
        for param in check_goodevents.keys():
        
            if len(np.intersect1d(df[param].values , check_goodevents[param])) > 0:
                is_goodevent = 1
        
    except:
        is_goodevent = 1
    

    return is_goodevent

'''
summary: window rule based stat model for last N second to make decision - >0 notify , 0 not notify
input:  df =                     %eventName  \
            eventTimestamp                                                           
            2020-10-29 19:17:09  broadcast   
            2020-10-29 19:22:52  broadcast   

                               eventParams  \
            eventTimestamp                                                           
            2020-10-29 19:17:09        {"action": "android.net.wifi.STATE_CHANGE"}   
            2020-10-29 19:22:52  {"action": "android.net.wifi.STATE_CHANGE", "n...   

                                 is_notify  
            eventTimestamp                  
            2020-10-29 19:17:09          0  
            2020-10-29 19:22:52          0  
output: 0
'''
def window_stats(df):
    
    dict_notify = {'broadcast' : 0,
                   'notification-channels' : 0,
                   'lifecycle-start' : 0,
                   'lifecycle-resume' : 0,
                   'lifecycle-create' : 0
                  }
    
    for f in dict_notify.keys():
        is_check = True if df[(df['eventName'] == f)].shape[0] > 0 else False
        if is_check:
            df_goodevents = df[(df['eventName'] == f)][:]
            is_f_notify = goodevents(df_goodevents , f)   
            dict_notify[f] = is_f_notify
        
    
    
    is_notify = check_notify(dict_notify)
    return is_notify

if __name__ == '__main__':
    #define seconds step for window check
    N_sec = 5

    dt_start = df_user.index.min()
    dt_end = df_user.index.max()

    dt_cur = dt_start



    while dt_cur <= dt_end:

        if df_user.loc[dt_cur:dt_next].shape[0] == 0:
            dt_cur = df_user[(df_user.index > dt_cur)].index.min()

        dt_next = dt_cur + datetime.timedelta(0,N_sec)


        print(f"{dt_cur} {  round(df_user.loc[dt_start:dt_cur].shape[0] / df_user.shape[0] , 4) }", end = '\r')

        df_user_part = df_user.loc[dt_cur:dt_next][:]

        is_notify = window_stats(df_user_part)
        df_user.loc[dt_cur:dt_next , 'is_notify'] = is_notify


        dt_cur = dt_next
    
    
