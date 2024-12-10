import os
import pandas as pd
import streamlit as st
from werkzeug.utils import secure_filename
from scripts import clean_phone_number  #Your cleaning function
import tempfile
from PIL import Image
import base64
import io
st.set_page_config(page_title='LIB Customer Phone', layout='wide',menu_items=None)

# --- Style ---
st.markdown(
    """
    <style>

    # .dvn-scroller{
    # top: 300px;
    # }
    
    # .stMain {
    # position:fixed;
    # width:900px;
    # }
    # .gdg-s1dgczr6{
    # width:900px;
    # background-color:blue

    # }
    # .st-emotion-cache-1wmy9hl{
    # position:fixed;
    # width:900px;
    
    # }
    # .gdg-s1dgczr6{
    # position:fixed;
    # top: 270px
    
    # }
    # .stFileUploader  {
    # position:fixed;
    # top: 270px;
    # }

        .header {
            background-color: #00BFFF;
            color: white;
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
            padding: 10px;
             position: relative;
             width:900px;
        }
        .nb {
            color: brown;
            margin-bottom: 10px;
        }
        .banner {
        top: 45px;
        position: fixed;
        left: 0;
        bottom: 5;
        width: 100%;
        background-color: #f1f1f1;
        text-align: center;
        font-size: 14px;
    }
        .container {
        
        }
        @media (max-width: 767px) {
    .header {
        flex-direction: column; /* Stack logo and text vertically */
        align-items: center;     /* Center items vertically */
        padding: 5px;
    }
    .header img {
        margin-bottom: 10px; /* Add bottom margin to separate logo and text */
        height: 50px;         /* Reduce logo size */
        width: auto;          /* Maintain aspect ratio */
    }
    .header h1 {
        text-align: center; /* Center the heading */
    }

    .container {
        flex-direction: column; /* Stack items vertically on smaller screens */
        align-items: center;
    }
}

/* Media query for medium screens (e.g., tablets) */
@media (min-width: 768px) and (max-width: 1023px) {
    .header {
        padding: 10px;
    }
    .header img {
        height: 50px;
    }
}

    </style>
    """,
    unsafe_allow_html=True,
)


# --- Header ---
try:
    logo_path = "images/images.jpg"  #Make sure this path is correct.
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
        # Read the file directly into a pandas DataFrame using Streamlit's functionality.
        if uploaded_file.name.endswith(('.xlsx','.xls')):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload XLS, XLSX, or CSV.")
            st.stop()

        df['phone'] = df['phone'].astype(str)
        df['phone'] = df['phone'].str.split('/')
        df = df.explode('phone')
        df['phone'] = df['phone'].str.replace('251', '0', 1)

        df['phone'] = df['phone'].str.split('.').str[0]

        if 'phone' in df.columns:
            df['phone'] = df['phone'].apply(clean_phone_number)
        else:
            st.error("Column 'phone' not found in the file.")
            st.stop()

        df = df[df['phone'].str.len() >= 8]
        df = df[(df['phone'].str.startswith('09')) & (df['phone'].str.len() == 10)]
        df['phone'] = df['phone'].str.strip()
        df = df.drop_duplicates(subset=['phone'])
        df.dropna(axis=1,inplace=True)
        # df = df[['phone']]


        # st.success("File processed successfully!")
        st.dataframe(df)     
         # Create an in-memory buffer to store the Excel file
        buffer = io.BytesIO()
        # Write the DataFrame to the in-memory buffer
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)

        # Set the file pointer to the beginning of the buffer
        buffer.seek(0)

        # Download the file
        st.download_button(
            label="Download data as XLSX",
            data=buffer,
            file_name='cleaned_phone.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='cleaned_phone.csv',
            mime='text/csv',
        )


    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

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

    