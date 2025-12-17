import os
import pandas as pd
import streamlit as st
from werkzeug.utils import secure_filename
from scripts import clean_phone_number  # Your cleaning function
import tempfile
from PIL import Image
import base64
import io
import re

st.set_page_config(page_title='LIB Customer Phone', layout='wide', menu_items=None)

# --- Style ---
st.markdown(
    """
    <style>
        .header {
            background-color: #333;
            color: white;
            padding: 5px; /* Reduced padding */
            text-align: left;
        }
        .header img {
            float: left;
            margin-right: 10px; /* Reduced margin */
            height: 60px;
        }
        .header h1 {
            margin-top: 10px; /*Reduced margin for h1*/
        }
        .content {
            background-color: powderblue;
            padding: 20px;
        }
        .nb {
            color: brown;
            margin-bottom: 10px;
        }
        .container {
            display: flex; /* Use flexbox for alignment */
            align-items: center; /* Vertically align items */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def find_phone_column(df):
    """
    Find phone-related columns in the dataframe
    Returns: List of column names that likely contain phone numbers
    """
    phone_keywords = [
        'phone', 'mobile', 'cell', 'tel', 'contact',
        'phonenumber', 'phonenum', 'phone_number', 'phone-number',
        'mobilenumber', 'mobilenum', 'mobile_number', 'mobile-number',
        'cellphone', 'cellnum', 'cell_number', 'cell-number',
        'telephone', 'contactnumber', 'contactnum'
    ]
    
    found_columns = []
    
    for col in df.columns:
        col_lower = str(col).lower()
        # Remove special characters for better matching
        clean_name = re.sub(r'[_\-\s]', '', col_lower)
        
        # Check for phone-related keywords
        for keyword in phone_keywords:
            clean_keyword = keyword.replace('_', '').replace('-', '')
            if (keyword == col_lower or 
                clean_keyword in clean_name or
                keyword.replace('_', '') in clean_name):
                found_columns.append(col)
                break
    
    return found_columns

def extract_phone_column(df, phone_col):
    """
    Extract and clean phone numbers from a column
    """
    # Convert to string and handle NaN
    df[phone_col] = df[phone_col].astype(str).fillna('')
    
    # Split by common separators
    separators = ['/', '&', 'or', '|', ',', ';', 'and']
    
    for sep in separators:
        df[phone_col] = df[phone_col].str.split(sep)
        df = df.explode(phone_col)
    
    # Clean common prefixes
    df[phone_col] = df[phone_col].str.replace('251', '0', 1, regex=False)
    df[phone_col] = df[phone_col].str.replace('+251', '0', 1, regex=False)
    
    # Remove anything after decimal point
    df[phone_col] = df[phone_col].str.split('.').str[0]
    
    # Apply custom cleaning function
    df[phone_col] = df[phone_col].apply(clean_phone_number)
    
    # Filter valid Ethiopian phone numbers
    df = df[df[phone_col].str.len() >= 8]
    df = df[(df[phone_col].str.startswith('09')) & (df[phone_col].str.len() == 10)]
    df[phone_col] = df[phone_col].str.strip()
    
    return df

# --- Header ---
try:
    logo_path = "images/images.jpg"  # Make sure this path is correct.
    logo = Image.open(logo_path)
    logo = logo.resize((100, 100))

    # Encode the image to Base64
    buffered = io.BytesIO()
    logo.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Create HTML with Base64 encoded image
    html = f""" 
        <div class='banner' style="display: flex; align-items: center; background-color: #00BFFF;color: white;">
            <img src="data:image/jpeg;base64,{img_str}" alt="Lion International Bank Logo" style="height: 60px;">
            <h2>Lion International Bank</h2>
            <h4>Phone Clearning </h4>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"Error: Logo image not found at {logo_path}.")
except Exception as e:
    st.error(f"An error occurred while displaying the logo: {e}")

# --- Content ---
st.markdown(
    """  
    <div class="content">
        <p class="nb">NB. : ፋይል አፕሎድ(Upload) ከማድረግዎ በፊት የስልክ ቁጥር የያዘውን አምድ(Column) ወደ phone ቀይረው ሴቭ(Save) ማድረግዎን እንዳይረሱ።:</p>
        """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Choose an Excel (.xlsx, .xls) or CSV (.csv) file", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    try:
        # Read the file directly into a pandas DataFrame
        if uploaded_file.name.endswith(('.xlsx','.xls')):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload XLS, XLSX, or CSV.")
            st.stop()
        
        # Show original columns
        st.info(f"File loaded successfully! Columns found: {list(df.columns)}")
        
        # Find phone columns
        phone_cols = find_phone_column(df)
        
        if not phone_cols:
            # If no phone columns found, let user select manually
            st.warning("No phone columns automatically detected. Please select the phone column manually:")
            selected_col = st.selectbox("Select phone column:", df.columns)
            phone_cols = [selected_col]
        elif len(phone_cols) > 1:
            # If multiple phone columns found, let user choose
            st.warning(f"Multiple phone columns detected: {phone_cols}")
            selected_col = st.selectbox("Select which column to clean:", phone_cols)
            phone_cols = [selected_col]
        else:
            # Single phone column found
            st.success(f"Phone column detected: '{phone_cols[0]}'")
        
        # Process the selected phone column
        phone_col = phone_cols[0]
        original_row_count = len(df)
        
        # Extract and clean phone numbers
        df = extract_phone_column(df, phone_col)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=[phone_col])
        
        # Remove empty columns
        df.dropna(axis=1, how='all', inplace=True)
        
        # Show statistics
        st.success(f"""
        Processing complete!
        - Original rows: {original_row_count}
        - Cleaned rows: {len(df)}
        - Removed duplicates: {original_row_count - len(df)}
        - Phone column used: '{phone_col}'
        """)
        
        # Display the cleaned dataframe
        st.dataframe(df.head(100))  # Show first 100 rows
        
        # Create download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Cleaned_Phone', index=False)
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download as Excel",
                data=buffer,
                file_name='cleaned_phone.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
        
        with col2:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name='cleaned_phone.csv',
                mime='text/csv',
                use_container_width=True
            )
        
        # Show column information
        with st.expander("📊 Data Information"):
            st.write(f"**Total rows:** {len(df)}")
            st.write(f"**Total columns:** {len(df.columns)}")
            st.write("**Columns:**", list(df.columns))
            st.write(f"**Sample phone numbers:**")
            st.write(df[phone_col].head(10).tolist())

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.exception(e)  # Show detailed error for debugging

# Footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        text-align: center;
        padding: 5px;
        font-size: 3px;
        height:30px
    }
    </style>
    <div class="footer">
        <p>© 2024  LIB phone Clearing and Formating - by Abreham Ashebir </p>
        <p><a href="https://anbesabank.com/" target="_blank">Anbesa Bank</a> | <a href="https://www.linkedin.com/company/lion-international-bank-s-c/posts/?feedView=all" target="_blank">Linkedin</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)