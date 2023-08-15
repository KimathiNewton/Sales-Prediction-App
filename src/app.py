# Importing Packages
import streamlit as st
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
import os
import pickle



# Function to load machine learning components
def load_components_func(fp):
    #To load the machine learning components saved to re-use in the app
    with open(fp,"rb") as f:
        object = pickle.load(f)
    return object


# Loading the machine learning components
DIRPATH = os.path.dirname(os.path.realpath(__file__))
ml_core_fp = os.path.join(DIRPATH,"Assets","Sales_Pred_model.pkl")
ml_components_dict = load_components_func(fp=ml_core_fp)



# Getting the encoder,scaler and model from the components dictionary

encoder = ml_components_dict['encoder']
imputer =ml_components_dict['imputer']
scaler = ml_components_dict['scaler']
model = ml_components_dict['model']

# Streamlit App
st.set_page_config(layout="centered")

st.title("Sales Forecast App for Corporation Favorita")
st.write("""Welcome to Corporation Favorita Sales Prediction app!
         This app allows you to predict the Sales for a specific 
         product in a chosen store at Corporation Favorita
     """)

#Image
st.image("https://images.startups.co.uk/wp-content/uploads/2023/05/sales-forecast.jpg?width=709&height=460&fit=crop")
with st.form(key="information",clear_on_submit=True):
    date = st.date_input("Date")
    Promotion = st.selectbox("On promotion,0 for No and 1 for Yes", [0, 1])
    transactions = st.number_input("Enter the number of transactions for the product")
    dcoilwtico = st.number_input("Enter the oil price (dcoilwtico)")

    products = st.selectbox('products', ['AUTOMOTIVE', 'BABY CARE', 'BEAUTY', 'BEVERAGES', 'BOOKS',
        'BREAD/BAKERY', 'CELEBRATION', 'CLEANING', 'DAIRY', 'DELI', 'EGGS',
        'FROZEN FOODS', 'GROCERY I', 'GROCERY II', 'HARDWARE',
        'HOME AND KITCHEN I', 'HOME AND KITCHEN II', 'HOME APPLIANCES',
        'HOME CARE', 'LADIESWEAR', 'LAWN AND GARDEN', 'LINGERIE',
        'LIQUOR,WINE,BEER', 'MAGAZINES', 'MEATS', 'PERSONAL CARE',
        'PET SUPPLIES', 'PLAYERS AND ELECTRONICS', 'POULTRY',
        'PREPARED FOODS', 'PRODUCE', 'SCHOOL AND OFFICE SUPPLIES',
        'SEAFOOD'])
    state = st.selectbox('state', ['Santa Elena', 'El Oro', 'Guayas'])
    city = st.selectbox('city',['Salinas', 'Machala', 'Libertad'])
    weeklysales = st.number_input("weekly Sales,0=Sun and 6=Sat", step=1)


    # Prediction
    if st.form_submit_button("predict"):
        # Dataframe Creation
        data = pd.DataFrame({
            "onpromotion": [Promotion],
            "transactions": [transactions],
            "dcoilwtico": [dcoilwtico],
            "date": [date],
            "family": [products],
            "state": [state],
            "weekly_sales": [weeklysales],
            "city": [city],

        })

        # Data Preprocessing
        
        # Converting date into datetime type
        data['date'] = pd.to_datetime(data['date'])
        
        
        # Feature Engineering
        #New features for the year, month and days
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.month
        data['day_of_month'] = data['date'].dt.day
        data['day_of_year'] = data['date'].dt.dayofyear
        data['Week'] = data['date'].dt.isocalendar().week
        data['day_of_week'] = data['date'].dt.dayofweek
        window = 7  
        data['transactions_rolling_avg'] = data['transactions'].rolling(window=window).mean()
        
        # Dropping the date column
        data = data.drop("date",axis=1)
    
        # Dividing numerical and categorical columns
        num_columns = data.select_dtypes(include=['int64', 'float64', 'int32', 'UInt32', 'int8']).columns
        cat_columns = data.select_dtypes(include=['object']).columns

        # Encoding Categorical columns
        encoded_data = encoder.transform(data[cat_columns])

        # Concatenate the encoded dataframe with the original dataframe
        df_encoded = pd.concat([data[num_columns], encoded_data], axis=1)
        df_encoded = df_encoded.reindex(columns=ml_components_dict['columns'])

        #Imputing the missing values
        data_imputed = imputer.transform(df_encoded)
            # Ensure columns are in the correct order
        data_scaled = data_imputed.copy()

        # Scale the numerical columns
        columns_to_scale = ['dcoilwtico', 'transactions', 'year', 'month', 'day_of_month',
                            'day_of_year', 'Week', 'day_of_week', 'transactions_rolling_avg']
        data_scaled[columns_to_scale] = scaler.transform(data_scaled[columns_to_scale])

        # Make prediction using the model
        predictions = model.predict(data_scaled)

        # Display the predictions
        st.balloons()
        # Display the predictions with custom styling
        st.success(f"Predicted Sales: {predictions[0]:,.2f}",icon="✅")


# Add a sidebar to the app
st.sidebar.title("Documentation and Help")

# Create a navigation menu within the sidebar
menu = st.sidebar.radio("Navigation", ["Introduction", "Getting Started", "User Guide", "Troubleshooting", "Feedback and Support"])
# Introduction
if menu == "Introduction":
    st.title("Introduction")
    st.write("Welcome to the Documentation and Help section of the Sales Prediction App. This section provides detailed instructions on how to use and understand the app effectively.")
# Getting Started
elif menu == "Getting Started":
    st.title("Getting Started")
    st.write("Before you can use the app, make sure you have Python and the required dependencies installed. Follow these steps:")
    st.code("""
    git clone https://github.com/yourusername/sales-prediction-app.git
    cd sales-prediction-app
    pip install -r requirements.txt
    streamlit run app.py
    """, language="bash")

# User Guide
elif menu == "User Guide":
    st.title("User Guide")
    st.write("The app requires the following input parameters for making sales predictions:")
    st.write("- **Date:** Select the date for which the sales took place.")
    st.write("- **On Promotion:** Choose whether the product is on promotion (1 for Yes, 0 for No).")
    st.write("- **Number of Transactions:** Enter the number of transactions for the product.")
    st.write("- **Oil Price (dcoilwtico):** Input the oil price for the selected date.")
    st.write("- **Product Category:** Choose the product category from the available options.")
    st.write("- **State:** Select the state where the store is located.")
    st.write("- **City:** Choose the city where the store is located.")
    st.write("- **Weekly Sales Day:** Enter the day of the week for which the sales occured (0 for Sunday, 1 for Monday, ..., 6 for Saturday).")

# Troubleshooting
elif menu == "Troubleshooting":
    st.title("Troubleshooting")
    st.write("Encountering issues while using the app? Here are some common troubleshooting steps:")
    st.write("- **Missing Data:** Ensure that you have provided values for all required input parameters.")
    st.write("- **Dependency Issues:** Make sure you have installed the necessary packages using the instructions provided in the installation section.")
    st.write("- **Scikit--learn:** The specified version of sckit--learn for this app is version 1.2.2")

# Feedback and Support
elif menu == "Feedback and Support":
    st.title("Feedback and Support")
    st.write("We value your feedback! If you have any questions, feedback, or issues, feel free to reach out to us via email:  newtonkimathi20@gmail.com or by [creating an issue](https://github.com/Newton23-nk/Sales-Prediction-App/issues) on the GitHub repository.")
    st.write("Connect With Me on LinkedIn:")
    st.write("[LinkedIn](https://www.linkedin.com/in/KimathiNewton/)") 
    st.write("Thank you for using the Sales Prediction App! We hope it provides valuable insights for your business decisions.")
    




