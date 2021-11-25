import os
import time
import logging

from pathlib import Path
import pandas as pd
import tkinter as tk

from tkinter import filedialog, messagebox
from tkinter.constants import END, FALSE

import sys

import time

class etl:
    def __init__(self,data_file,dimension_dir,output_file_dir,delimiter=None):
        self.data_file = data_file
        self.dimension_dir = dimension_dir
        self.output_file_dir = output_file_dir
        self.delimiter = delimiter
        self.errors=[]
    def validation(self):
        self.validation_status=True
        self.output_file_ind=False
        for idx,file_obj in enumerate([self.data_file,self.dimension_dir,self.output_file_dir]):
            try:
                my_file=None
                file_obj_len= len(file_obj)
                if file_obj_len > 0 and idx != 2:
                   my_file = Path(file_obj)
                if (not my_file or not my_file.is_file()) and  idx == 0:
                    self.errors.append("Invalid Source File Path: ,please try with right data File")
                    self.validation_status=False
                elif (not my_file or not my_file.is_dir()) and  idx == 1:
                    self.errors.append("Invalid Dimension File Path ,please try with correct dimension directory")
                    self.validation_status=False  
                elif  idx == 2:
                   if not  Path(os.path.dirname(file_obj)).is_dir():
                       self.validation_status=False
                       self.errors.append("Ouput File path is Wrong or empty ")
                   elif Path(file_obj).is_file():
                       self.validation_status = True
                       self.output_file_ind= True
                   elif Path(file_obj).is_dir():
                       self.output_file_ind= False
                   else:
                       self.output_file_ind= True  
            except Exception as e:
                if idx == 0:
                    self.errors.append("Invalid Source File Path: ,please try with right data File:"+str(e))
                elif idx == 1:
                    self.errors.append("Invalid Dimension File Path ,please try with correct dimension directory:"+str(e))
                elif idx == 2:
                    self.errors.append("Invalid Output File Path ,please try with correct output directory:"+str(e))
                self.validation_status=False                
    def transform(self):
        logging.info('processing data .........')
        # Creating the metadata dictionary
        self.transform_status=True
        try:
            obj_file= os.listdir(self.dimension_dir)
            obj_dictmap = {'key':'value'}
            obj_trgfile ={}
            self.obj_lst=list()
            
            for ifile,files in enumerate(obj_file):
                # new change delimiter=self.delimiter
                obj_mbrs = pd.Series(data=(pd.read_csv(self.dimension_dir+'\\'+files,delimiter=self.delimiter,usecols=[0],squeeze=True))).drop_duplicates()
                # Creating dictionary
                for i,ele in enumerate(obj_mbrs):
                   obj_dictmap[ele]=ifile
            
            dcol =len(self.data_file)

            with open(self.data_file,buffering=300000) as f:
                for line in f:
                    line = line.strip().split(sep=self.delimiter) # new change self.delimiter
                    for each in line:
                        each = each.strip('"')
                        if each in obj_dictmap:
                            obj_trgfile.pop(obj_dictmap[each],None)
                            row = (obj_dictmap[each], str(each))
                            obj_trgfile[obj_dictmap[each]]=each
                        else:
                            obj_trgfile[dcol]=each
            
            
                    # change for enclosing double quotes 
                    line_items=[]
                    for x in sorted(obj_trgfile):
                        item=str(obj_trgfile[x])
                        if not item.isdigit():
                            item='"'+item+'"'
                        line_items.append(item)   
                    line=','.join(line_items)
                    
                    #line = ','.join(str(obj_trgfile[x]) for x in sorted(obj_trgfile))
                    self.obj_lst.append(line)
        except Exception as e:
            self.errors.append("Processing Error="+str(e))
            self.transform_status=False
    def load(self,df_static_cols_dict=None):
        self.load_status=True
        try:
            obt_df=pd.DataFrame(self.obj_lst)
            if df_static_cols_dict:
               for k,v in df_static_cols_dict.items():
                   obt_df[k]=v
            obt_df=pd.DataFrame(self.obj_lst)
            logging.info(f'data frame conatins {obt_df.shape[0]} Rows and {obt_df.shape[1]} columns')
            data=obt_df.to_string(header=False, index=False)
            if self.output_file_ind:
                final_data="\n".join([line.lstrip() for line in data.split("\n")])
                with open(self.output_file_dir,"w") as file:
                    file.write(final_data)
            else:
                final_data="\n".join([line.lstrip() for line in data.split("\n")])
                with open(self.output_file_dir,"w") as file:
                    file.write(final_data)
        except Exception as e:
            self.errors.append("Load Output File Error="+str(e))
            self.load_status=False



log_file=os.path.abspath("logs")+"\\data_converter.log"
logging.basicConfig(filename=log_file, filemode='w',format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info('Admin logged in')

if len(sys.argv) >= 4:
       elt_obj=etl(data_file=sys.argv[1],dimension_dir=sys.argv[2],output_file_dir=sys.argv[3])
       
       elt_obj.validation()

       if elt_obj.validation_status:
           elt_obj.transform()
           if elt_obj.transform_status:
               elt_obj.load()
               if  elt_obj.load_status:
                  logging.info('output_file generated in the directory:'+sys.argv[3])
               else:
                  logging.info('errors:'+str(elt_obj.errors))
           else:
                logging.info('errors:'+str(elt_obj.errors))
       else:
          logging.info('errors:'+str(elt_obj.errors))
elif  len(sys.argv)-1 > 1:
       logging.info("provide all three mandatory inputs  source_file,dimension_directory,output_directory")

else:
    #-------------------------------variables---------------------------------
    about="""Data Converter Tool Process unstructured data and convert to Structured formate.\n
            
            1. Tool Acccept Txt and CSV formates.
            2. Tool can generate Fine output to Csv and TXT format.
            
        """
    column_box_list = []
    value_box_list = []
    column_del_list=[]
    column_label_list=[]
    value_label_list=[]
    btn_idx =[]
    columns=[]
    values=[]
    
    
    column_names=[]
    value_names=[]
    i=0
    # -----------------------------Root Window --------------------------------
    root = tk.Tk()
    root.geometry("1100x650")   
    root.title('Data Converter Tool')
    root.config(background='#efefef')
    root.iconbitmap(os.path.join(os.getcwd(),'logo.ico'))
    
    #------------------------------Manu Bar-------------------------------------
    menubar = tk.Menu(root, background="#eb98c7")
    
    def about_popup():
        messagebox.showinfo(title="About Data Converter Tool", message=about, icon=messagebox.INFO)
    
    menubar.add_command(label="About", command=about_popup)
    menubar.add_command(label="Quit!", command=root.quit)   
    root.config(menu=menubar)  
    
    #-------------------------------------------------labels -----------------------
    # we can not refere this lable, because we are not placeing or configaring in root window
    source_file_label = tk.Label(root, 
                      text = "Source File :-",
                      fg='#00586b',
                      bg='#efefef').place(x = 10, y = 30)  
        
    dimension_file_label = tk.Label(root, 
                          text = "Dimension File Path :-",
                          fg='#00586b',
                          bg='#efefef').place(x = 10,y = 60) 
    
    output_file_label = tk.Label(root, 
                          text = "Output File :-",
                          fg='#00586b',
                          bg='#efefef').place(x = 10,y = 90) 
    delimiter_label = tk.Label(root, 
                          text = "Delimiter :-",
                          fg='#00586b',
                          bg='#efefef').place(x = 10,y =120)
    
    #------------------------------------input box---------------------------------
    souce_text_box=tk.Entry(root, width=93,fg='#00586b',bg='#ffffff')
    souce_text_box.place(x=160, y =30)
    
    dimension_text_box=tk.Entry(root, width=93,fg='#00586b',bg='#ffffff')
    dimension_text_box.place(x=160, y =60)
    
    output_text_box=tk.Entry(root, width=93,fg='#00586b',bg='#ffffff')
    output_text_box.place(x=160, y =90)
    
    delimiter_text_box=tk.Entry(root, width=30,fg='#00586b',bg='#ffffff')
    delimiter_text_box.place(x=160, y =120)
    
    #-----------------------------------------buttions------------------------------
    Source_file_button = tk.Button(root, text="Browse File..", width= 20, bg='#0097e6',fg='#ffffff',command=lambda:source_file_browser())
    Source_file_button.place(x=730, y=26)
    
    clear_all_button= tk.Button(root, text="Clear All", width= 20,height=2, bg='#0097e6',fg='#ffffff',command=lambda:clear_all())
    clear_all_button.place(x=890, y=37)
    
    dimension_folder_button = tk.Button(root, text="Browse Folder..", width= 20,bg='#0097e6',fg='#ffffff', command=lambda:dimension_folder_browser())
    dimension_folder_button.place(x=730, y=56)
    
    output_file_button = tk.Button(root, text="Browse Folder..", width= 20, bg='#0097e6',fg='#ffffff', command=lambda:output_folder_browser())
    output_file_button.place(x=730, y=86)
    
    add_colmn_Button = tk.Button(root, text='Add Columns +',width= 20, bg='#0097e6',fg='#ffffff', command=lambda:addBox())
    add_colmn_Button.place(x=380, y =115)
    
    submit_button= tk.Button(root, text="Submit", width= 20, bg='#0097e6',fg='#ffffff',command=lambda:process_data())
    submit_button.place(x=550, y=115)
    
    # -------------------------------------app functions----------------------------------------
    def about_popup():
        messagebox.showinfo(title="About", message=about, icon=messagebox.INFO)
        
    def source_file_browser():
        souce_text_box.delete(0, END)
        input_path=filedialog.askopenfilename(filetypes =[('Text Files','*.txt'),('All Files', '*.*')])
        if input_path:
            souce_text_box.insert(0,input_path)
        else:
            souce_text_box.insert(0 , "please Select source file path ..")
        return None
    
    def dimension_folder_browser():
        dimension_text_box.delete(0, END)
        input_path=filedialog.askdirectory()
        if input_path:
            dimension_text_box.insert(0,input_path)
        else:
            dimension_text_box.insert(0 ,"please Select Dimension folder path..")
        return None
        
    def output_folder_browser():
        output_text_box.delete(0, END)
        input_path=filedialog.askdirectory()
        if input_path:
            output_text_box.insert(0,input_path)
        else:
            output_text_box.insert(0 ,"please Select Output  file or folder path..")
        return None
    def clear_all():
        souce_text_box.delete(0, END)
        dimension_text_box.delete(0, END)
        output_text_box.delete(0, END)    
    
    def _delete_colums(j):
        global i
        i=0
        for colmnname in column_box_list:
            column_names.append(colmnname.get())
        for valuename in value_box_list:
            value_names.append(valuename.get())
        
        column_names.pop(j)
        value_names.pop(j)
    
        if column_box_list:
            for box in column_box_list:
                box.destroy()
            column_box_list.clear()
    
            for value_box in value_box_list:
                value_box.destroy()
            value_box_list.clear()  
    
            for label in column_box_list:
                label.destroy()
            column_box_list.clear()
    
            for label in column_label_list:
                label.destroy()
            column_label_list.clear()
    
            for label in value_label_list:
                label.destroy()
            value_label_list.clear()
    
            for del_btn in column_del_list:
                del_btn.destroy()
            no_of_buttons_add=len(column_del_list)-1
            column_del_list.clear()
            for i in range(no_of_buttons_add):
                addBox(column_names[i],value_names[i])
            column_names.clear()
            value_names.clear()
    
        else:
            pass
    
    def addBox(column_name=None,column_value=None):
        global i
        # get length of last generate box to place new Entry box
        next_column = len(column_box_list)
        j=0
        if next_column<=19:
            if not column_box_list:
                column_position=delimiter_text_box.place_info()['y']
                column_position=int(column_position)+10
            else:
                column_position =value_box_list[-1].place_info()['y']
            
            y_position = int(column_position) +27
            column_lable= tk.Label(root, 
                            text = f"Column {str(next_column+1)}:-",
                            fg='#00586b',
                            bg='#efefef')
            column_lable.place(x = 50,y =y_position)
    
            value_lable= tk.Label(root, 
                            text = f"Value:-",
                            fg='#00586b',
                            bg='#efefef')
            value_lable.place(x = 410,y =y_position)
    
        # Y position is dinamic
            column_box = tk.Entry(root,fg='#00586b',bg='#ffffff')
            column_box.place(x=160, y=y_position,width=180,height=23)
            if column_name:
                column_box.insert(0,column_name)
    
            Value_box = tk.Entry(root,fg='#00586b',bg='#ffffff')
            Value_box.place(x= 500, y=y_position,width=180,height=23)
            if column_value:
                Value_box.insert(0,column_value)
            j=i
            btn_idx.append(i)
            delete_Button = tk.Button(root, text='Delete',width= 10,bg='#0097e6',fg='#ffffff', command=lambda:_delete_colums(j))
            delete_Button.place(x=700, y =y_position)
            i=i+1
    
            column_box_list.append(column_box )
            value_box_list.append(Value_box)
            column_label_list.append(column_lable)
            value_label_list.append(value_lable)
            column_del_list.append(delete_Button)
    
        else:
            msg= "20 Columns are the Limit, application can not add more that "
            messagebox.showinfo(title="Info", message=msg, icon=messagebox.ERROR)
        
    
    def process_data():
        logging.info('processing data .........')
        validation_status = True
        output_file_ind = True
        obj_dictmap = {'key':'value'}
        obj_trgfile ={}
        #df = pd.DataFrame()
        obj_lst=list()
        df_static_cols_dict={}
        
        data_file = souce_text_box.get()
        dimension_dir = dimension_text_box.get()
        output_file_dir = output_text_box.get()
        
        # new change
        delimiter=delimiter_text_box.get()
        
        _delimiter=None if delimiter.strip() == "" else delimiter
    
        
        if not Path(data_file).is_file():
            validation_status=False
            messagebox.showinfo(title="Warning", message="Source File path is Wrong or empty ", icon=messagebox.ERROR)
        elif not Path(dimension_dir).is_dir(): 
            validation_status=False
            messagebox.showinfo(title="Warning", message="Dimention Folder path is Wrong or empty ", icon=messagebox.ERROR)
        elif output_file_dir:
            if not  Path(os.path.dirname(output_file_dir)).is_dir():
                validation_status=False
                output_file_ind = FALSE
                messagebox.showinfo(title="Warning", message="Ouput File path is Wrong or empty ", icon=messagebox.ERROR)
            elif Path(output_file_dir).is_file():
                validation_status = True
                output_file_ind= True
            elif Path(output_file_dir).is_dir():
                output_file_ind= False
            else:
                output_file_ind= True
        # new change commented below validation
        '''
        if not _delimiter:
            validation_status=False
            messagebox.showinfo(title="Warning", message=" please select Delimiter  ", icon=messagebox.ERROR)
        '''
        
        try:
            if validation_status:
                process_data_lable= tk.Label(root, 
                    text = f"Processing your Request..",
                    fg='#f5368c',
                    bg='#efefef')
                process_data_lable.place(x = 410,y =2)
                root.update()
                dimension_file= os.listdir(dimension_dir)
                for ifile,files in enumerate(dimension_file):
                    obj_mbrs = pd.Series(data=(pd.read_csv(dimension_dir+'/'+files,delimiter=_delimiter,usecols=[0],squeeze=True))).drop_duplicates()
    
                    # Creating dictionary
                    for i,ele in enumerate(obj_mbrs):
                        obj_dictmap[ele]=ifile
    
                dcol =len(dimension_file)
    
                if column_box_list:
                    for col_value in column_box_list: 
                        columns.append(col_value.get())
                    for value in value_box_list:
                        values.append(value.get())
                    df_static_cols_dict=dict(zip(columns,values))
                with open(data_file,buffering=300000) as f:
                    for line in f:
                        line = line.strip().split(sep=_delimiter) # new change
                        for each in line:
                            each = each.strip('"')
                            if each in obj_dictmap:
                                obj_trgfile.pop(obj_dictmap[each],None)
                                row = (obj_dictmap[each], str(each))
                                obj_trgfile[obj_dictmap[each]]=each
                            else:
                                obj_trgfile[dcol]=each
                                
                                
                        # change for enclosing double quotes 
                        line_items=[]
                        for x in sorted(obj_trgfile):
                            item=str(obj_trgfile[x])
                            if not item.isdigit():
                                item='"'+item+'"'
                            line_items.append(item)   
                        line=','.join(line_items)
    
                        #line = ','.join(str(obj_trgfile[x]) for x in sorted(obj_trgfile))
                        obj_lst.append(line)
                obt_df=pd.DataFrame(obj_lst)
                logging.info(f'data frame conatins {obt_df.shape[0]} Rows and {obt_df.shape[1]} columns')
                if df_static_cols_dict:
                    for k,v in df_static_cols_dict.items():
                        obt_df[k]=v
                data=obt_df.to_string(header=False, index=False)
                
                if output_file_ind:
                    final_data="\n".join([line.lstrip() for line in data.split("\n")])
                    with open(output_file_dir,"w") as file:
                        file.write(final_data)
                    folder=os.path.dirname(output_file_dir)
                    messagebox.showinfo(title="Info", message=f" file Success Fully created in to this folder \n {folder}", icon=messagebox.INFO)
                    process_data_lable.destroy()
                else:
                    final_data="\n".join([line.lstrip() for line in data.split("\n")])
                    with open(output_file_dir+"/output.txt", "w") as file:
                        file.write(final_data)
                    messagebox.showinfo(title="Info", message=f" file Success Fully created in to this folder \n {output_file_dir}", icon=messagebox.INFO)
                    process_data_lable.destroy()
                logging.info('data processing completed.........')
            else:
                pass
        except Exception as e:
            msg="Processing Error="+str(e)
            logging.error(e)
            messagebox.showinfo(title="Warning", message=msg, icon=messagebox.ERROR)
    root.mainloop()
