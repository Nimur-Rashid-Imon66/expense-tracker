import os
import streamlit as st
import pandas as pd

from src.db_ops import show_data, edit_data, delete_data,select_columns,extra_field


def save_expense(cursor, db):    
    st.header('💸 Expense Entry')
    if 'flag' not in st.session_state:
        st.session_state.flag = 0

    df = pd.read_sql('''SELECT * FROM expense''', con=db)
    column_names,column_types = extra_field(df,db)
    col = select_columns(db)
    
    
    with st.form(key='expense_submit_form', clear_on_submit=True, border=True):
        
        expense_category = ['Shopping', 'Snacks', 'Mobile Recharge', 
                            'Online Course', 'Subscription', 'Others']
        
        values = []
        st3 = []
        expense_date = st.date_input('Expense Date*')
        values.append(expense_date)
        
        category = st.selectbox('Expense Category*', expense_category)
        values.append(category)
        
        amount = st.text_input('Amount*')
        values.append(amount)
        
        notes = st.text_area('Notes')
        values.append(notes)
        
        # st.write(column_types)
        for column_name, column_type in zip(column_names, column_types):
            if "varchar(512)" in column_type:  # Handle VARCHAR types
                value = st.text_input(column_name)
                st3.append(value)
            elif column_type == "double":
                value = st.number_input(column_name)
                st3.append(value)
            elif column_type in ("longtext", "TEXT"):  # Group text types
                value = st.text_area(column_name)
                st3.append(value)
            elif "date" in column_type:  # Handle both DATE and TIMESTAMP
                value = st.date_input(column_name)
                st3.append(value)
            elif "timestamp" in column_type:  # Handle both DATE and TIMESTAMP
                value = st.date_input(column_name)
                st3.append(value)
            else:
                st.write(f"Unsupported type for {column_name}: {column_type}")
                
        document_upload = st.file_uploader('Upload Document', 
                                           type=['txt','pdf', 
                                                 'jpg', 'png', 'jpeg'], 
                                            accept_multiple_files=True)
        # st.write(values)
        if st.form_submit_button(label='Submit'):
            if not(expense_date and category and amount):
                st.error('Please fill all the * fields')
            else:
                st.session_state.flag = 1
                # st.success('Data Submitted Successfully')


    if st.session_state.flag:
        # st.write(final_parameter_calculation)

        with st.form(key='final', clear_on_submit=True, border=True):
             # st.write(final_parameter_calculation)

            if st.form_submit_button('Are you Sure?'):
                # st.write(final_parameter_calculation)
                st.session_state.flag = 0
                all_documents = []
                for file in document_upload:
                    if file is not None:
                        # Get the file name and extract the extension
                        file_name = file.name
                        # st.write(file_name)
                        file_extension = os.path.splitext(file_name)[1]
                        dir_name = "./documents/expenses"
                        if not os.path.isdir(dir_name):
                            os.makedirs(dir_name)

                        file_url = dir_name + '/' + file_name
                        # file_url = dir_name + file_name
                        all_documents.append(file_url)
                        xyz = ", ".join(all_documents)
                        # st.write(str(xyz))
                        values.append(str(xyz))
                        for x in range(len(st3)):
                            values.append(st3[x])
                        # st.write(str(values))
                        # val = str(all_documents)
                        
                        # Save the file in its original format
                        with open(file_url, "wb") as f:
                            f.write(file.read())
                        st.success("File has been successfully saved.")
         

                # query = '''Insert into expense (expense_date, category, amount, 
                #                                 notes, documents) 
                #         VALUES (%s, %s, %s, %s, %s)
                #         '''
                # values = (expense_date, category, amount, notes, str(all_documents))
                
                column_names_placeholders = ", ".join(col)
                value_placeholders = ", ".join(["%s"] * len(values))
                
                # Construct  Updated the SQL query
                query = f"INSERT INTO expense ({column_names_placeholders}) VALUES ({value_placeholders})"

                # st.write(query, values)
                cursor.execute(query, tuple(values))
                db.commit()
                st.success("Expense Record Inserted Successfully!")
                st.balloons()

            else:
                st.write("Click above button If you are Sure")
    else:
        st.warning("Please fill up above form")

    df = pd.read_sql('''SELECT * FROM expense''', con=db)
    
    col = select_columns(db)
    show_data(df,col)
    edit_data(cursor, db,col, df,  'Edit Expenses', 'expense')
    delete_data(cursor, db,col, df, 'Delete Expenses', 'expense')


def parameter_listing(cursor, db):
    st.header('⚙️🛠️ Parameter Addition')
    with st.form(key='add_parameter_form', clear_on_submit=True, border=True):
        all_data_type = ['VARCHAR(512)', 'double', 
                            'longtext', 'DATE','TIMESTAMP']
        parameter_name = st.text_input('Parameter Name*')
        data_type = st.selectbox('Expense Category*', all_data_type)
        if st.form_submit_button(label='Submit'):
            if not(parameter_name and data_type):
                st.error('Please fill all the * fields')
            else:
                query = f"ALTER TABLE expense ADD {parameter_name} {data_type}"
                # st.write(query, values)
                cursor.execute(query)
                db.commit()
                st.success("Parameter Inserted Successfully!")
                st.balloons()        
