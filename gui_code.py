#prototype code
import sys
import PySimpleGUI as sg

import os
import pandas as pd
import networkx as nx
#import matplotlib.pyplot as plt

import itertools
from pyvis.network import Network
import warnings

from sqlalchemy import create_engine
import pandas as pd

db_connection_str = 'mysql+pymysql://mysql_user:mysql_password@mysql_host/mysql_db'
db_connection = create_engine(db_connection_str)

df_circle = pd.read_sql('SELECT distinct(circle)as circle FROM data', con=db_connection)
circle_name_list=df_circle['circle'].tolist()

df_vendor = pd.read_sql('SELECT vendor,circle FROM data group by vendor', con=db_connection)
#vendor_name_list=df_circle['circle'].tolist()

warnings.filterwarnings("ignore", 'This pattern has match groups')
main_path=os.getcwd()
#import pyautogui  width, height= pyautogui.size()  print(width)  print(height)
pd.options.mode.chained_assignment = None


circle_name_list=['IND','CAL','ILL']
circle_dict={
    'huawei' : ['IND','CAL','FLO'],
    'eci' : ['ILL','IND','FLO'],
    }
        
def load_cn_data(df):
    df=df[['en1', 'en2', 'rt']]
    df[["SON","SOP"]]=df['en1'].str.split(':',n=1,expand=True)
    df[["SIN","SIP"]]=df['en2'].str.split(':',n=1,expand=True)
    df=df[["SON","SOP", "SIN","SIP", "rt"]]
    return df

def load_an_data(df):
    df=df[["SON","SOP", "SIN","SIP", "Level"]]
    df.rename(columns = {'Level':'rt'}, inplace = True)
    return df

def load_data(circle,vendor):
    os.chdir(main_path)
    try:
        print("Circle ==>",str(circle).upper(),"::","Vendor ==>",str(vendor).upper())
        print("="*125)
        chg=circle+'\\'+vendor
        isExist = os.path.exists(chg)
        if isExist :
            os.chdir(chg)
            if os.path.isfile('links.xlsx'):
                global df
                df = pd.read_excel(r"links.xlsx",sheet_name='Sheet1')
                df=df.apply(lambda x: x.astype(str).str.upper())
                if str(vendor).upper() == 'CN':
                    df=load_cn_data(df)
                elif str(vendor).upper() == 'AN':
                    df=load_an_data(df)
                return True
            else:
                return False
        else:
            cirexist=os.path.exists(circle)
            if not cirexist :
                os.makedirs(circle)
                os.chdir(circle)
                os.makedirs(vendor)
                return False
            else:
                venexist=os.path.exists(vendor)
                if not venexist :
                    os.chdir(circle)
                    os.makedirs(vendor)
                    return False
    except:
        return ("Error")
        
def create_graph(filt_val):
    if filt_val == "":
        filt_df=df
    else:
        filt_df=df[df['rt'].str.contains(filt_val, na=False)]
    filt_df['so']=filt_df["SON"].copy()
    filt_df['ta']=filt_df["SIN"].copy()
    filt_df['s_port']=filt_df["SOP"].copy()
    filt_df['t_port']=filt_df["SIP"].copy()
    sheet1=filt_df
    sheet6=sheet1["so"]
    sheet7=sheet1["ta"]
    dt=pd.DataFrame([])
    dt = pd.concat([sheet6,sheet7],axis=0, ignore_index = True)
    #print(dt)
    dt=dt.drop_duplicates()
    node_names=dt.to_list()
    Graphtype = nx.Graph()
    G = nx.from_pandas_edgelist(filt_df, edge_attr=["s_port","t_port"], create_using=Graphtype)
    G.add_nodes_from(node_names)
    return filt_df,G

def node_list_to_edge_list(a):
    edge_list=[]
    attrs={}
    counter=0
    while counter < len(a)-1:
        so=a[counter]
        ta=a[counter+1]
        lis=[so,ta]
        tup=tuple(lis)
        edge_list.append(tup)
        counter+=1
    return edge_list

def plot_graph(ind,gr):
    plt_g=nx.Graph()
    plt_g.add_nodes_from(gr)
    edge_list=node_list_to_edge_list(gr)
    plt_g.add_edges_from(edge_list)
    nx.draw(plt_g, with_labels=True)
    nt = Network('600px', '1000px',notebook=False)
    nt.from_nx(plt_g)
    fig_name=ind+'.html'
    nt.show(fig_name)
    #plt.show()

def list_of_vendors(val):
    list_of_keys = [key
                    for key, list_of_values in circle_dict.items()
                    if val in list_of_values]
    return list_of_keys

def network_gui():
    circle_confirm_flag=0
    network_conf_flag=0
    def clear_circle_vendor():
        window['circle'].update(value='')
        window['vendor'].update(value='')
    
    def clear_all_data():
        window['so'].update(value='')
        window['ta'].update(value='')
        window['S_LIST'].update(visible=False)
        window['T_LIST'].update(visible=False)
        window ['plot_graph']. Update (value = False)

    def icon_visible():
        window['S_LIST'].update(visible=False)
        window['T_LIST'].update(visible=False)
        window['ta'].update(visible=True)
        window['so'].update(visible=True)
        values['so']=''
        values['ta']=''
        
    so_list=[]
    ta_list=[]
    sg.theme('BluePurple')
    function_list_column = [
            [sg.Text('Circle',size=(20, 1), font=('Lucida',11,'bold'),justification='left')],
            [sg.Combo(circle_name_list,size=(15, 1),enable_events=True,key='circle')],
            [sg.Text('Vendor ',size=(30, 1), font=('Lucida',11,'bold'),justification='left')],
            [sg.Combo([],size=(15,1),key='vendor')],
            [sg.Button('Confirm', font=('Times New Roman',12)),sg.Button('Clear', font=('Times New Roman',12))],
            [sg.Text('Layer rt ',size=(30, 1), font=('Lucida',11,'bold'),justification='left')],
            [sg.Combo(['MDM','ETH','MST','PTK'],size=(15,1),enable_events=True,key='domain')],
            [sg.Button('Configure Network', font=('Times New Roman',12))],
            [sg.Text('Function',size=(30, 1), font=('Lucida',11,'bold'),justification='left')],
            [sg.Listbox(values=['SP'],
                        select_mode='extended', enable_events=True, key='fac', size=(30, 6))],
            
    ]

    content_viewer_column = [
        [sg.Text('Inputs',font=('Lucida',11,'bold'),size=(10,1))],
        [sg.Text('Node A',font=('Lucida',11,'bold'), size=(10,1)), sg.Input(do_not_clear=True , enable_events=True, key='so')],
        [sg.Listbox(so_list, size=(40,3),auto_size_text=True,visible=False, enable_events=True, key='S_LIST')],
        [sg.Text('Node Z',font=('Lucida',11,'bold'), size=(10,1)), sg.InputText(do_not_clear=True , enable_events=True,key='ta')],
        [sg.Listbox(ta_list, size=(40,3),auto_size_text=True,visible=False, enable_events=True, key='T_LIST')],
        [sg.Checkbox('Plot Graph',key='plot_graph')],
        
        ]

    result_viewer_row = [
        [sg.Text('Result',font=('Lucida',11,'bold'),)],
        [sg.Output(size=(131,14), font='Courier 12')],
        ]

    # ----- Full layout -----
    layout = [
        [
            sg.Column(function_list_column),
            sg.VSeperator(),
            sg.Column(content_viewer_column),
            #sg.VSeperator(),
            #sg.Column([[sg.Image(r'png',size=(200, 180))]])    
        ],
        [sg.Button('RUN', font=('Times New Roman',12)),
         sg.Button('CANCEL', font=('Times New Roman',11)),
         sg.Button('CLEAR_ALL', font=('Times New Roman',11)),
  ],
        [sg.HSeparator()],
        [result_viewer_row],
    ]

    window = sg.Window("SMP", layout,icon=r'png').Finalize()
    window.Maximize()

    while True:
        event, values = window.read()
        strx=""
        for val in values['fac']:
            strx=strx+ " "+ val+","

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "CANCEL" or event == sg.WIN_CLOSED:
            break  
        elif event =='circle':
            list_of_keys = [key
                        for key, list_of_values in circle_dict.items()
                        if values[event] in list_of_values]
            window['vendor'].update(value='', values=list_of_keys)
        elif event == "Clear":  # A file was chosen from the listbox
            clear_circle_vendor()
        elif event =='Confirm':
            clicked =sg.PopupOKCancel('Once Confirmed Circle and Vendor cananot be altered')
            if clicked == 'OK':
                circle_confirm_flag=1
                if values['circle'] == '' or values['vendor'] == '' :
                    sg.popup("Please select Circle and Vendor to Confirm")
                else:
                    s=load_data(values['circle'],values['vendor'])
                    if s is True:
                        sg.popup("Circle and Vendor specific link data is loaded")
                        window['circle'].update(disabled=True)
                        window['vendor'].update(disabled=True)
                        window['Clear'].update(disabled=True)
                        window['Confirm'].update(disabled=True)
                        
                    else:
                        sg.popup("Link Data is not present cannot be loaded")
                        clear_circle_vendor()
            if clicked == 'Cancel':
                pass
                    
        elif event=='Configure Network':
            network_conf_flag=1
            clear_all_data()
#            if values['circle'] == '' or values['vendor']=='' and circle_confirm_flag == 1:
            if circle_confirm_flag == 1:
                filt_val=str(values['domain']).upper()
                filt_df,G=create_graph(filt_val)
                sg.popup("Level filtered with ",values['domain'],"No of links are",len(filt_df))
                so_list=filt_df["SON"].drop_duplicates()
                ta_list=filt_df["SIN"].drop_duplicates()
                
            else:
                sg.popup("Please load proper Vendor's Circle data before going forword")
                
        elif event=='fac':
            if network_conf_flag == 1:
                clear_all_data()
                #clear_all_data()
                window ['plot_graph'].update(disabled=False)
                window['so'].update(value='')
                window['so'].update(disabled=False)
                window['ta'].update(value='')
                window['ta'].update(disabled=False)
                window['S_LIST'].update(visible=False)
                window['T_LIST'].update(visible=False)
            else:
                sg.popup("Please configure network before going forword")

        if event == 'so':
            if values['so'] != '':                         # if a keystroke entered in search field
                window['S_LIST'].update(visible=True)
                window['T_LIST'].update(visible=False)
                search = values['so']
                new_values = [x for x in so_list if search.upper() in x]  # do the filtering
                window.Element('S_LIST').Update(new_values)# display in the listbox
                
        if event == 'S_LIST' and len(values['S_LIST']):     # if a list item is chosen
           window.Element('so').Update(values['S_LIST'])
           window['S_LIST'].update(visible=False)
           sg.Popup('Selected so or A end', values['S_LIST'])
        if event == 'ta':
            if values['ta'] != '':                         # if a keystroke entered in search field
                window['S_LIST'].update(visible=False)
                window['T_LIST'].update(visible=True)
                search = values['ta']
                new_values = [x for x in ta_list if search.upper() in x]  # do the filtering
                window.Element('T_LIST').Update(new_values)# display in the listbox

        if event == 'T_LIST' and len(values['T_LIST']):     # if a list item is chosen
           window.Element('ta').Update(values['T_LIST'])
           window['T_LIST'].update(visible=False)
           sg.Popup('Selected ta or Z end ', values['T_LIST'])
                
        elif event =='CLEAR_ALL':
            window['so'].update(value='')
            window['ta'].update(value='')
            window['S_LIST'].update(visible=False)
            window['T_LIST'].update(visible=False)
            window ['plot_graph']. Update (value = False)
           
        elif event == "RUN" :  # A file was chosen from the listbox
            window['T_LIST'].update(visible=False)
            if strx[1:len(strx)-1]=='SP':
                if values['so'] =='' or values['ta'] =='':
                    sg.popup('for shartest path you have to give A end and Z end i.e so and ta respectively')
                else:
                    sg.popup('Options Chosen',      
                'Your Selected Circle is: '+ values['circle'] + ' of vendor: '+values['vendor'] + '\n with Layer rt: '+values['domain']
                         +' \nYour function is: Shortest Path'
                         +'\n so is :'+values['so'] +'\n ta is :'+values['ta'])
                    s= values['so']
                    s=s.strip("('',)")
                    t=values['ta']
                    t=t.strip("('',)")
                    a=nx.shortest_path(G,s,t)
                    len_a=nx.shortest_path_length(G,s,t)
                    print("The Shortest path length is : ",len_a)
                    print('-'*125)
                    print("The Shortest path between",s ," and ",t,"is :\n",a)
                    print('='*125)
                        
                    if values['plot_graph']==True:
                        plot_graph(ind='Shortest_Path',gr=a)
                        window ['plot_graph']. Update (value = False)
            else:
                sg.popup_error("Please select function or Enter valid input")
    window.close()

if __name__ == '__main__':
    network_gui()
