import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from transformers import AutoImageProcessor, AutoModelForImageClassification
import joblib
import numpy as np
import torch
from PIL import Image,ImageDraw,ImageEnhance
from sklearn.cluster import KMeans
import cv2
from ultralytics import YOLO
import os
import time
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase,VideoProcessorBase,WebRtcMode
import av
import time
import random
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def summarize_detections(detected_objects):
    df = pd.DataFrame(detected_objects, columns=['Class', 'Confidence'])
    df_summary = df.groupby('Class').agg({
        'Confidence': ['mean', 'count']
    }).reset_index()
    df_summary.columns = ['Class', 'Avg_Confidence', 'Count']
    return df_summary


def plot_detection_summary(df_summary):
    fig = px.bar(df_summary, x='Class', y='Count', 
                 hover_data=['Avg_Confidence'],
                 labels={'Count': 'Number of Detections', 'Avg_Confidence': 'Avg Confidence'},
                 title='Detection Summary')
    fig.update_traces(marker_color=df_summary['Avg_Confidence'], 
                      marker_colorbar=dict(title='Avg Confidence'))
    st.plotly_chart(fig)

def predict_other_with_confidence(image, processor, model, labels):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1)[0]
    predicted_class_idx = probabilities.argmax().item()
    confidence = probabilities[predicted_class_idx].item()
    return labels[predicted_class_idx], confidence


def simulated_ml_process(steps=5, duration=3):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(steps):
        progress = (i + 1) / steps
        progress_bar.progress(progress)
        status_text.text(f"Processing step {i+1}/{steps}: {random.choice(['Feature extraction', 'Model inference', 'Post-processing', 'Confidence calculation'])}")
        time.sleep(duration / steps)
    
    progress_bar.empty()
    status_text.empty()

def confidence_visualization(confidence, class_name):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Confidence score", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100]},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': confidence * 100}}))
    st.plotly_chart(fig)



def apply_scanning_effect_and_process(image, model_func, *args):
    image_placeholder = apply_scanning_effect(image)
    
    with st.spinner("Processing image..."):
        simulated_ml_process()
    
    # Clear the image placeholder after scanning effect
    image_placeholder.empty()
    
    result = model_func(image, *args)
    
    # Check if the result is from a YOLO model (tuple with two elements, second element is a list)
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], list):
        # YOLO model result, don't display confidence gauge
        return result
    elif isinstance(result, tuple) and len(result) in [2, 3]:
        # Other models with confidence (including soil nutrition)
        if len(result) == 2:
            class_name, confidence = result
        else:  # soil nutrition case
            _, class_name, confidence = result
        confidence_visualization(confidence, class_name)
    
    return result


# Load configuration from YAML file
config_path = './config.yaml'

if os.path.exists(config_path):
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
else:
    config = {
        'credentials': {
            'usernames': {}
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'some_signature_key',
            'name': 'some_cookie_name'
        },
        'pre-authorized': {  # Add this key
            'emails': []     # Empty list for pre-authorized emails
        }
    }

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
    # Remove the pre-authorized parameter from here
)

def save_config():
    with open(config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def registration_page():
    st.title("New User Registration")
    with st.form("registration_form"):
        username = st.text_input("Username")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        repeat_password = st.text_input("Repeat Password", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            if password == repeat_password:
                if username not in config['credentials']['usernames']:
                    try:
                        # Use the correct parameter format for the newer version
                        authenticator.register_user(
                            fields={
                                'username': username,
                                'name': name,
                                'password': password,
                                'email': email,
                                # Add any other fields you want
                            },
                            pre_authorized=False,
                            location='main'  # Add location parameter
                        )
                        # Manually add phone number since it's not a standard field
                        config['credentials']['usernames'][username]['phone'] = phone
                        save_config()
                        st.success("Registration successful. You can now log in.")
                    except Exception as e:
                        st.error(f"Error during registration: {e}")
                else:
                    st.error("Username already exists. Please choose a different username.")
            else:
                st.error("Passwords do not match.")

def init_session_state():
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None

def login_page():
    st.title("AI Assistant for Plant and Soil")
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        fields = {
            'username': 'Username',
            'password': 'Password',
            'login': 'Login'
        }
        
        # Call login without expecting return values (newer version behavior)
        authenticator.login(fields=fields, location='main')
        
        # Check authentication status from session state
        if st.session_state.get('authentication_status'):
            # User is authenticated - get details from session state
            st.session_state['name'] = st.session_state.get('name')
            st.session_state['username'] = st.session_state.get('username')
            # st.experimental_rerun()
            st.rerun()
        elif st.session_state.get('authentication_status') is False:
            st.error('Username/password is incorrect')
        elif st.session_state.get('authentication_status') is None:
            st.warning('Please enter your username and password')
    
    with register_tab:
        registration_page()

def main_app():
    st.sidebar.success(f"Welcome {st.session_state['name']}!")
    if authenticator.logout('Logout', 'sidebar', key='logout_sidebar'):
        st.session_state['authentication_status'] = None
        st.rerun()
    st.sidebar.title('Navigation')
    pages = {
        "Home": home_page,
        "Soil Nutrition": soil_nutrition_page,
        "Plant Disease Identification": plant_disease_page,
        "Cotton Pests Identification": cotton_pests_page,
        "Tomato Ripeness Detection": fruit_ripeness_page,
        "Banana Ripeness Detection": yolo_page,
        "Mango Ripeness Detection": mango_ripeness_page
    }
    page = st.sidebar.selectbox("Go to", list(pages.keys()))
    
    
    
    # Call the selected page function
    pages[page]()

save_path = './soil_nutritionv2'

captured_image = None

def apply_scanning_effect(image):
    image_placeholder = st.empty()
    scanning_image = image.copy()
    width, height = scanning_image.size
    
    for y in range(0, height, 10):
        scanning_overlay = scanning_image.copy()
        draw = ImageDraw.Draw(scanning_overlay)
        draw.line([(0, y), (width, y)], fill="lime", width=5)
        scanning_overlay = scanning_overlay.convert("RGB")
        enhancer = ImageEnhance.Brightness(scanning_overlay)
        scanning_overlay = enhancer.enhance(1.2)
        
        image_placeholder.image(scanning_overlay, caption='Scanning Image...', width=300)
        time.sleep(0.05)
    
    return image_placeholder  


class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame = None

    def recv(self, frame):
        self.frame = frame.to_ndarray(format="bgr24")
        return av.VideoFrame.from_ndarray(self.frame, format="bgr24")

@st.cache_resource
def load_model(model_name):
    if model_name == "Plant disease":
        processor = AutoImageProcessor.from_pretrained("A2H0H0R1/swin-tiny-patch4-window7-224-plant-disease-new")
        model = AutoModelForImageClassification.from_pretrained("A2H0H0R1/swin-tiny-patch4-window7-224-plant-disease-new")
    elif model_name == "Cotton Pests":
        processor = AutoImageProcessor.from_pretrained("RohithN2004/Cotton-pests")
        model = AutoModelForImageClassification.from_pretrained("RohithN2004/Cotton-pests")
    elif model_name == "Fruit Ripeness":
        model = YOLO(r'.\train43\weights\best.pt')
        processor = None
    elif model_name == "YOLO":
        model = YOLO(r'.\train11\weights\best.pt')
        processor = None
    elif model_name == "mango":
        model = YOLO(r'.\train51\weights\best.pt')
        processor = None
    elif model_name == "Soil Nutrition":
        best_regressor_model = joblib.load(os.path.join(save_path, 'best_regressor_model.pkl'))
        best_classifier_model = joblib.load(os.path.join(save_path, 'best_classifier_model.pkl'))
        le = joblib.load(os.path.join(save_path, 'label_encoder.pkl'))
        model = (best_regressor_model, best_classifier_model, le)
        processor = None
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    return processor, model

crops = {
    'Alluvial soil': {
        'Distribution': "Alluvial soils cover about 46% of India's total area, mainly in the Indo-Gangetic-Brahmaputra plains, except for a few places where the top layer is covered by desert sand. They also occur in deltas of the Mahanadi, Godavari, Krishna, and Cauvery rivers, as well as in the Narmada and Tapi valleys and northern parts of Gujarat.",
        'Characteristics': "These soils are immature and have weak profiles due to their recent origin. They are mostly sandy and clayey, with pebbly and gravelly soils being rare. The soil is porous due to its loamy nature, providing good drainage and conditions favorable for agriculture.",
        'Chemical Properties': "Alluvial soils have low nitrogen levels but adequate levels of potash, phosphoric acid, and alkalies. Iron oxide and lime levels vary widely.",
        'Suitable Crops': ['Rice', 'Wheat', 'Sugarcane', 'Tobacco', 'Cotton', 'Jute', 'Maize', 'Oilseeds', 'Vegetables', 'Fruits'],
        'Color and Texture': "The color of alluvial soil is light grey or ash grey, and its texture is sandy to silty loam or clay."
    },
    'Black soil': {
        'Distribution': "Black soils are typical of the Deccan trap region, covering parts of Maharashtra, Saurashtra, Malwa, Madhya Pradesh, and Chattishgarh, as well as extending into the Godavari and Krishna valleys.",
        'Characteristics': "These soils are made up of clayey soil and are well-known for their capacity to hold moisture. They develop wide cracks during the dry season but are resistant to wind and water erosion due to their iron-rich granular structure.",
        'Chemical Properties': "Black soils are poor in humus but highly moisture-retentive, responding well to irrigation.",
        'Suitable Crops': ['Sugarcane', 'Paddy', 'Wheat', 'Cereal crops', 'Pulse crops'],
        'Color and Texture': "Black soils are black in color and have a clayey texture."
    },
    'Red soil': {
        'Distribution': "Red soils are found in areas of low rainfall in the eastern and southern parts of the Deccan plateau, as well as in parts of Odisha, Chhattisgarh, West Bengal, Maharashtra, southern Karnataka, Tamil Nadu, and Madhya Pradesh.",
        'Characteristics': "Red soils develop a reddish color due to the diffusion of iron in crystalline and metamorphic rocks. They are porous and friable in structure.",
        'Chemical Properties': "Red soils are deficient in lime, kankar (impure calcium carbonate), and have adequate levels of lime, phosphate, manganese, nitrogen, humus, and potash.",
        'Suitable Crops': ['Wheat', 'Cotton', 'Pulses', 'Tobacco', 'Oilseeds', 'Potatoes'],
        'Color and Texture': "Red soils have a reddish color and a sandy to clay and loamy texture."
    },
    'Clay soil': {
        'Distribution': "Clay soils are not a distinct type of soil in India, but rather a component of various soil types, including alluvial, black, and red soils.",
        'Characteristics': "Clay soils are typically found in areas with high rainfall and are known for their ability to retain moisture and nutrients.",
        'Chemical Properties': "Clay soils have varying levels of nutrients depending on the specific type of soil they are a part of.",
        'Suitable Crops': ['Wheat', 'Cotton','Sorghum','Maize','Barley'],
        'Color and Texture': "Clay soils have a dark brown to black color and a clayey texture."
    }
}

pest_info = {
                "American Bollworm": {
                    "Description": "The American bollworm (Helicoverpa armigera) is a major pest of cotton, causing significant damage to the crop. It is a nocturnal moth with a distinctive white stripe on its forewings.",
                    "Life Cycle": "The life cycle of American bollworm consists of four stages: egg, larva, pupa, and adult. Eggs are laid on the leaves and stems of the cotton plant. Larvae feed on the leaves, flowers, and bolls, causing significant damage. Pupae are formed in the soil, and adults emerge after about 10 days.",
                    "Seasonality": "American bollworm is active throughout the year, but its population peaks during the cotton flowering and fruiting stages.",
                    "Control Methods": "Chemical control methods include insecticides like deltamethrin, lambda-cyhalothrin, and chlorpyriphos. Non-chemical methods include crop rotation, biological control using natural predators, and cultural practices like pruning and removing weeds.",
                    "Economic Threshold": "The economic threshold for American bollworm is typically set at 5-6 larvae per plant, beyond which control measures are necessary to prevent significant damage to the crop."
                },
                "Cotton Aphid": {
                    "Description": "The cotton aphid (Aphis gossypii) is a sap-sucking insect that feeds on the sap of cotton plants. It is a small, soft-bodied insect with a distinctive black and yellow coloration.",
                    "Life Cycle": "Cotton aphids have a complex life cycle involving multiple generations. Eggs are laid on the leaves and stems of the cotton plant, and nymphs emerge after about 3-4 days. Nymphs go through several instars before reaching adulthood, which takes about 10-14 days.",
                    "Seasonality": "Cotton aphids are most active during the cotton flowering and fruiting stages, when the plant is producing sap.",
                    "Control Methods": "Chemical control methods include insecticides like pyrethroids and organophosphates. Non-chemical methods include biological control using natural predators, cultural practices like pruning and removing weeds, and introducing beneficial insects like ladybugs.",
                    "Economic Threshold": "The economic threshold for cotton aphids is typically set at 10-15 aphids per leaf, beyond which control measures are necessary to prevent significant damage to the crop."
                },
                "Pink Bollworm": {
                    "Description": "The pink bollworm (Pectinophora gossypiella) is a major pest of cotton, causing significant damage to the crop. It is a nocturnal moth with a distinctive pinkish color.",
                    "Life Cycle": "The life cycle of pink bollworm consists of four stages: egg, larva, pupa, and adult. Eggs are laid on the bolls of the cotton plant. Larvae feed on the bolls, causing significant damage. Pupae are formed in the soil, and adults emerge after about 10 days.",
                    "Seasonality": "Pink bollworm is most active during the cotton flowering and fruiting stages, when the plant is producing bolls.",
                    "Control Methods": "Chemical control methods include insecticides like deltamethrin, lambda-cyhalothrin, and chlorpyriphos. Non-chemical methods include crop rotation, biological control using natural predators, and cultural practices like pruning and removing weeds.",
                    "Economic Threshold": "The economic threshold for pink bollworm is typically set at 5-6 larvae per plant, beyond which control measures are necessary to prevent significant damage to the crop."
                },
                "Red Cotton Bug": {
                    "Description": "The red cotton bug (Dysdercus koenigii) is a major pest of cotton, causing significant damage to the crop. It is a nocturnal bug with a distinctive red color.",
                    "Life Cycle": "The life cycle of red cotton bug consists of four stages: egg, nymph, and adult. Eggs are laid on the leaves and stems of the cotton plant. Nymphs go through several instars before reaching adulthood, which takes about 10-14 days.",
                    "Seasonality": "Red cotton bug is most active during the cotton flowering and fruiting stages, when the plant is producing sap.",
                    "Control Methods": "Chemical control methods include insecticides like pyrethroids and organophosphates. Non-chemical methods include biological control using natural predators, cultural practices like pruning and removing weeds, and introducing beneficial insects like ladybugs.",
                    "Economic Threshold": "The economic threshold for red cotton bug is typically set at 10-15 bugs per plant, beyond which control measures are necessary to prevent significant damage to the crop."
                },
                "Spotted Bollworm": {
                    "Description": "The spotted bollworm (Earias vittella) is a major pest of cotton, causing significant damage to the crop. It is a nocturnal moth with a distinctive white spot on its forewings.",
                    "Life Cycle": "The life cycle of spotted bollworm consists of four stages: egg, larva, pupa, and adult. Eggs are laid on the leaves and stems of the cotton plant. Larvae feed on the leaves, flowers, and bolls, causing significant damage. Pupae are formed in the soil, and adults emerge after about 10 days.",
                    "Seasonality": "Spotted bollworm is most active during the cotton flowering and fruiting stages, when the plant is producing bolls.",
                    "Control Methods": "Chemical control methods include insecticides like deltamethrin, lambda-cyhalothrin, and chlorpyriphos. Non-chemical methods include crop rotation, biological control using natural predators, and cultural practices like pruning and removing weeds.",
                    "Economic Threshold": "The economic threshold for spotted bollworm is typically set at 5-6 larvae per plant, beyond which control measures are necessary to prevent significant damage to the crop."
                },
                "Thrips": {
                    "Description": "Thrips (Thrips tabaci) are small, sap-sucking insects that feed on the sap of cotton plants. They are a major pest of cotton, causing significant damage to the crop.",
                    "Life Cycle": "Thrips have a complex life cycle involving multiple generations. Eggs are laid on the leaves and stems of the cotton plant, and nymphs emerge after about 3-4 days. Nymphs go through several instars before reaching adulthood, which takes about 10-14 days.",
                    "Seasonality": "Thrips are most active during the cotton flowering and fruiting stages, when the plant is producing sap.",
                    "Control Methods": "Chemical control methods include insecticides like pyrethroids and organophosphates. Non-chemical methods include biological control using natural predators, cultural practices like pruning and removing weeds, and introducing beneficial insects like ladybugs.",
                    "Economic Threshold": "The economic threshold for thrips is typically set at 10-15 thrips per leaf, beyond which control measures are necessary to prevent significant damage to the crop."
                },
                "Whitefly": {
                    "Description": "Whiteflies (Bemisia tabaci) are small, sap-sucking insects that feed on the sap of cotton plants. They are a major pest of cotton, causing significant damage to the crop.",
                    "Life Cycle": "Whiteflies have a complex life cycle involving multiple generations. Eggs are laid on the leaves and stems of the cotton plant, and nymphs emerge after about 3-4 days. Nymphs go through several instars before reaching adulthood, which takes about 10-14 days.",
                    "Seasonality": "Whiteflies are most active during the cotton flowering and fruiting stages, when the plant is producing sap.",
                    "Control Methods": "Chemical control methods include insecticides like pyrethroids and organophosphates. Non-chemical methods include biological control using natural predators, cultural practices like pruning and removing weeds, and introducing beneficial insects like ladybugs.",
                    "Economic Threshold": "The economic threshold for whiteflies is typically set at 10-15 whiteflies per leaf, beyond which control measures are necessary to prevent significant damage to the crop."
                }
            }

disease_info = {
                'Apple___Apple_scab': {
                    'Reason': 'Apple scab is caused by the fungus Venturia inaequalis, which thrives in cool, wet conditions. It enters the apple through natural openings or wounds and spreads rapidly through the tree, causing scab-like lesions on the fruit and leaves.',
                    'Treatment': 'Apply fungicides to the tree during the growing season to prevent infection. Remove infected leaves and fruit to prevent the spread of the disease. Maintain good air circulation around the tree to reduce humidity.',
                    'Good Conditions': 'Plant apple trees in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Apple___Black_rot': {
                    'Reason': 'Black rot is caused by the fungus Botryosphaeria obtusa, which enters the apple through wounds and thrives in warm, humid conditions. It spreads rapidly through the tree, causing black lesions on the fruit and leaves.',
                    'Treatment': 'Remove infected fruit and leaves to prevent the spread of the disease. Apply fungicides to the tree during the growing season. Maintain good air circulation around the tree to reduce humidity.',
                    'Good Conditions': 'Plant apple trees in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Apple___Cedar_apple_rust': {
                    'Reason': 'Cedar apple rust is caused by the fungus Phyllactinia guttata, which thrives in cool, moist conditions. It enters the apple through natural openings or wounds and causes rust-like lesions on the fruit and leaves.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply fungicides to the tree during the growing season. Maintain good air circulation around the tree to reduce humidity.',
                    'Good Conditions': 'Plant apple trees in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Apple___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant apple trees in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Blueberry___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant blueberries in acidic, well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Cherry_(including_sour)___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant cherries in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Cherry_(including_sour)___Powdery_mildew': {
                    'Reason': 'Powdery mildew is caused by the fungus Erysiphe polygoni, which thrives in warm, humid conditions. It enters the cherry through natural openings or wounds and causes a powdery coating on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply fungicides to the tree during the growing season. Maintain good air circulation around the tree to reduce humidity.',
                    'Good Conditions': 'Plant cherries in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': {
                    'Reason': 'Cercospora leaf spot is caused by the fungus Cercospora zeae-maydis, which thrives in warm, humid conditions. It enters the corn through natural openings or wounds and causes small, circular lesions on the leaves.',
                    'Treatment': 'Remove infected leaves to prevent the spread of the disease. Apply fungicides to the corn during the growing season. Maintain good air circulation around the corn to reduce humidity.',
                    'Good Conditions': 'Plant corn in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Corn_(maize)___Common_rust_': {
                    'Reason': 'Common rust is caused by the fungus Puccinia sorghi, which thrives in warm, humid conditions. It enters the corn through natural openings or wounds and causes yellow or orange spots on the leaves.',
                    'Treatment': 'Remove infected leaves to prevent the spread of the disease. Apply fungicides to the corn during the growing season. Maintain good air circulation around the corn to reduce humidity.',
                    'Good Conditions': 'Plant corn in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Corn_(maize)___Northern_Leaf_Blight': {
                    'Reason': 'Northern leaf blight is caused by the fungus Cercospora zeae-maydis, which thrives in warm, humid conditions. It enters the corn through natural openings or wounds and causes large, irregular lesions on the leaves.',
                    'Treatment': 'Remove infected leaves to prevent the spread of the disease. Apply fungicides to the corn during the growing season. Maintain good air circulation around the corn to reduce humidity.',
                    'Good Conditions': 'Plant corn in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Corn_(maize)___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant corn in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Grape___Black_rot': {
                    'Reason': 'Black rot is caused by the fungus Botryosphaeria obtusa, which enters the grape through wounds and thrives in warm, humid conditions. It spreads rapidly through the vine, causing black lesions on the fruit and leaves.',
                    'Treatment': 'Remove infected fruit and leaves to prevent the spread of the disease. Apply fungicides to the vine during the growing season. Maintain good air circulation around the vine to reduce humidity.',
                    'Good Conditions': 'Plant grapes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Grape___Esca_(Black_Measles)': {
                    'Reason': 'Esca is caused by the fungus Phomopsis viticola, which thrives in warm, humid conditions. It enters the grape through natural openings or wounds and causes black lesions on the fruit and leaves.',
                    'Treatment': 'Remove infected fruit and leaves to prevent the spread of the disease. Apply fungicides to the vine during the growing season. Maintain good air circulation around the vine to reduce humidity.',
                    'Good Conditions': 'Plant grapes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {
                    'Reason': 'Leaf blight is caused by the fungus Isariopsis clavispora, which thrives in warm, humid conditions. It enters the grape through natural openings or wounds and causes small, circular lesions on the leaves.',
                    'Treatment': 'Remove infected leaves to prevent the spread of the disease. Apply fungicides to the vine during the growing season. Maintain good air circulation around the vine to reduce humidity.',
                    'Good Conditions': 'Plant grapes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Grape___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant grapes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Orange___Haunglongbing_(Citrus_greening)': {
                    'Reason': 'Huanglongbing is caused by the bacterium Candidatus Liberibacter asiaticus, which is transmitted by the psyllid Diaphorina citri. It enters the orange through the psyllid and causes yellowing of the leaves and fruit.',
                    'Treatment': 'Remove infected trees to prevent the spread of the disease. Apply insecticides to control psyllids. Maintain good air circulation around the tree to reduce humidity.',
                    'Good Conditions': 'Plant oranges in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Peach___Bacterial_spot': {
                    'Reason': 'Bacterial spot is caused by the bacterium Xanthomonas arboricola, which thrives in warm, humid conditions. It enters the peach through natural openings or wounds and causes small, circular lesions on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply bactericides to the tree during the growing season. Maintain good air circulation around the tree to reduce humidity.',
                    'Good Conditions': 'Plant peaches in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Peach___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant peaches in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Pepper,_bell___Bacterial_spot': {
                    'Reason': 'Bacterial spot is caused by the bacterium Xanthomonas arboricola, which thrives in warm, humid conditions. It enters the pepper through natural openings or wounds and causes small, circular lesions on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply bactericides to the plant during the growing season. Maintain good air circulation around the plant to reduce humidity.',
                    'Good Conditions': 'Plant peppers in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Pepper,_bell___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant peppers in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Potato___Early_blight': {
                    'Reason': 'Early blight is caused by the fungus Alternaria solani, which thrives in warm, humid conditions. It enters the potato through natural openings or wounds and causes small, circular lesions on the leaves and tubers.',
                    'Treatment': 'Remove infected leaves and tubers to prevent the spread of the disease. Apply fungicides to the potato during the growing season. Maintain good air circulation around the potato to reduce humidity.',
                    'Good Conditions': 'Plant potatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Potato___Late_blight': {
                    'Reason': 'Late blight is caused by the fungus Phytophthora infestans, which thrives in cool, moist conditions. It enters the potato through natural openings or wounds and causes large, irregular lesions on the leaves and tubers.',
                    'Treatment': 'Remove infected leaves and tubers to prevent the spread of the disease. Apply fungicides to the potato during the growing season. Maintain good air circulation around the potato to reduce humidity.',
                    'Good Conditions': 'Plant potatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Potato___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant potatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Raspberry___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant raspberries in acidic, well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Soybean___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant soybeans in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Squash___Powdery_mildew': {
                    'Reason': 'Powdery mildew is caused by the fungus Erysiphe polygoni, which thrives in warm, humid conditions. It enters the squash through natural openings or wounds and causes a powdery coating on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply fungicides to the squash during the growing season. Maintain good air circulation around the squash to reduce humidity.',
                    'Good Conditions': 'Plant squash in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Strawberry___Leaf_scorch': {
                    'Reason': 'Leaf scorch is caused by the fungus Colletotrichum acutatum, which thrives in warm, humid conditions. It enters the strawberry through natural openings or wounds and causes small, circular lesions on the leaves.',
                    'Treatment': 'Remove infected leaves to prevent the spread of the disease. Apply fungicides to the strawberry during the growing season. Maintain good air circulation around the strawberry to reduce humidity.',
                    'Good Conditions': 'Plant strawberries in acidic, well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Strawberry___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant strawberries in acidic, well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Bacterial_spot': {
                    'Reason': 'Bacterial spot is caused by the bacterium Xanthomonas arboricola, which thrives in warm, humid conditions. It enters the tomato through natural openings or wounds and causes small, circular lesions on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply bactericides to the tomato during the growing season. Maintain good air circulation around the tomato to reduce humidity.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Early_blight': {
                    'Reason': 'Early blight is caused by the fungus Alternaria solani, which thrives in warm, humid conditions. It enters the tomato through natural openings or wounds and causes small, circular lesions on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply fungicides to the tomato during the growing season. Maintain good air circulation around the tomato to reduce humidity.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Late_blight': {
                    'Reason': 'Late blight is caused by the fungus Phytophthora infestans, which thrives in cool, moist conditions. It enters the tomato through natural openings or wounds and causes large, irregular lesions on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply fungicides to the tomato during the growing season. Maintain good air circulation around the tomato to reduce humidity.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Leaf_Mold': {
                    'Reason': 'Leaf mold is caused by the fungus Fusarium oxysporum, which thrives in warm, humid conditions. It enters the tomato through natural openings or wounds and causes small, circular lesions on the leaves.',
                    'Treatment': 'Remove infected leaves to prevent the spread of the disease. Apply fungicides to the tomato during the growing season. Maintain good air circulation around the tomato to reduce humidity.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Septoria_leaf_spot': {
                    'Reason': 'Septoria leaf spot is caused by the fungus Septoria lycopersici, which thrives in warm, humid conditions. It enters the tomato through natural openings or wounds and causes small, circular lesions on the leaves.',
                    'Treatment': 'Remove infected leaves to prevent the spread of the disease. Apply fungicides to the tomato during the growing season. Maintain good air circulation around the tomato to reduce humidity.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Spider_mites Two-spotted_spider_mite': {
                    'Reason': 'Spider mites are caused by the mite Tetranychus urticae, which thrives in warm, dry conditions. It enters the tomato through natural openings or wounds and causes small, circular lesions on the leaves.',
                    'Treatment': 'Apply insecticides to the tomato during the growing season. Remove infested leaves to prevent the spread of the disease. Maintain good air circulation around the tomato to reduce humidity.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Target_Spot': {
                    'Reason': 'Target spot is caused by the fungus Corynespora cassiicola, which thrives in warm, humid conditions. It enters the tomato through natural openings or wounds and causes small, circular lesions on the leaves and fruit.',
                    'Treatment': 'Remove infected leaves and fruit to prevent the spread of the disease. Apply fungicides to the tomato during the growing season. Maintain good air circulation around the tomato to reduce humidity.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
                    'Reason': 'Tomato yellow leaf curl virus is caused by the virus Tomato yellow leaf curl virus, which is transmitted by the whitefly Bemisia tabaci. It enters the tomato through the whitefly and causes yellowing of the leaves and fruit.',
                    'Treatment': 'Remove infected plants to prevent the spread of the disease. Apply insecticides to control whiteflies.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___Tomato_mosaic_virus': {
                    'Reason': 'Tomato mosaic virus is caused by the virus Tomato mosaic virus, which is transmitted through infected soil, water, or tools. It causes mottled or mosaic patterns on the leaves and fruit.',
                    'Treatment': 'Remove infected plants to prevent the spread of the disease. Disinfect tools and equipment used on infected plants. Rotate crops to prevent soil buildup of the virus.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                },
                'Tomato___healthy': {
                    'Reason': 'No disease present.',
                    'Treatment': 'None needed.',
                    'Good Conditions': 'Plant tomatoes in well-draining soil with full sun. Maintain a balanced fertilizer schedule and prune regularly to promote air circulation and reduce humidity.'
                }
            }

# Prediction functions
def predict_yolo(image, model, conf_threshold, iou_threshold):
    results = model(image, conf=conf_threshold, iou=iou_threshold)
    result_image = results[0].plot()
    detected_objects = []
    for box in results[0].boxes:
        class_id = int(box.cls)
        confidence = float(box.conf)
        detected_objects.append((model.names[class_id], confidence))
    return result_image, detected_objects



def predict_soil_nutrition(image, models):
    regressor_model, classifier_model, label_encoder = models
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    smoothed_image = cv2.GaussianBlur(image, (5, 5), 0)
    reshaped_image = smoothed_image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=3, random_state=0).fit(reshaped_image)
    dominant_color = kmeans.cluster_centers_[0]
    predicted_pH = regressor_model.predict([dominant_color])[0]
    predicted_soil_type_proba = classifier_model.predict_proba([dominant_color])[0]
    predicted_soil_type_encoded = np.argmax(predicted_soil_type_proba)
    predicted_soil_type = label_encoder.inverse_transform([predicted_soil_type_encoded])[0]
    confidence = predicted_soil_type_proba[predicted_soil_type_encoded]
    return predicted_pH, predicted_soil_type, confidence

def predict_other(image, processor, model, labels):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()
    return labels[predicted_class_idx]

# Home page content
def home_page():
    st.title('Grow with Confidence: Introducing AI Personal Assistant for Plant and Soil ')
    

    st.markdown("""
    Ever looked at your garden and wondered, "Is my soil healthy?" or "What's that spot on my tomato plant?"  Well, wonder no more! We're excited to introduce a revolutionary tool that empowers to become an expert in our own backyard.
    """)
    
    st.image(".\\Pictures\\Home page\\Gemini_Generated_Image_h7i8v7h7i8v7h7i8.jpeg")
    st.markdown("""
    Our user-friendly application takes the guesswork out of plant care, providing valuable insights into the soil's health and potential plant problems. With just a few clicks, we can gain the knowledge that we need to nurture our plants and ensure a bountiful harvest.
    """)
    st.markdown("""
    Here's how our app helps in cultivatating a thriving garden:
    """)
    st.subheader("1.Unveiling the Secrets of Your Soil:")
    
    st.markdown("""
    Soil pH Analysis: Struggling to understand those cryptic soil test kits? Our app simplifies the process! Simply upload a picture of the soil, and our advanced image processing technology will analyze its color to determine its pH level, ingredients and humidity of soil. Knowing the soil's pH is crucial, as it directly affects the nutrients available to the plants. With this information, one can make informed decisions about amending the soil to create the perfect environment for the plants to flourish.
    """)

    st.subheader("2.Identifying Plant Diseases:")
    st.markdown("""
    Early Detection is Key: Spotting plant diseases early is vital for saving your precious crops. Our app acts as a personal plant doctor, using image recognition to identify various diseases affecting a wide range of plants, including tomatoes, peppers, and apple trees. With a clear diagnosis, one can take swift action to treat the problem and protect their harvest.
    """)

    st.subheader("3.Recognizing Cotton Field Threats:")
    st.markdown("""
    Protecting the Cotton Crop: Cotton farmers face unique challenges when it comes to protecting their crops from pests. Our app utilizes image recognition technology to identify common cotton pests like aphids and bollworms. By equipping this knowledge, one can take appropriate measures to control pest populations and ensure a healthy, high-yielding cotton harvest.
    """)

    st.subheader("4.Ensuring Perfectly Ripened Fruit:")
    st.markdown("""
   Harvesting at the Peak of Flavor: Knowing exactly when to pick fruits can be tricky. Our app takes the guesswork out of fruit ripening, specifically focusing on bananas,tomatoes and mangoes. Using advanced image recognition, the app can analyze a picture of a banana and determine its ripeness. This ensures one can enjoy the fruits at their peak of sweetness and flavor.
    """)

    st.subheader("Developed with Cutting-Edge Technology:")

    st.markdown("""
                Our app leverages the power of artificial intelligence and machine learning to deliver these incredible features.  We've trained our models on massive datasets of images, allowing to accurately analyze photos and provide reliable results.
    """)

    st.markdown("""
    Technologies:\n
        Hugging Face\n 
        YOLO model
    
        """)
    # st.markdown("""
    # Plant Disease and Cotton Pest Identification: These features utilize a vast dataset of images sourced from Hugging Face, a leading platform for AI resources.
    
    #     """)
    # st.markdown("""
        
    #     Fruit Ripeness Detection: This functionality is powered by the YOLO model, a highly regarded object detection algorithm.
    #         """)
# Soil Nutrition page content
def soil_nutrition_page():
    st.title("Know Your Soil's Secrets: Unlock the Key to Plant Health")
    st.header(' Analyze Your Soil Today!')
    st.markdown("""
    Having healthy soil is the foundation of a thriving garden. But understanding complex soil test kits can be challenging. Our app simplifies the process!
    """)
    st.markdown("""
    Our "Soil pH Analysis" feature uses image recognition to analyze the color of your soil from a simple picture.
    """)
    st.markdown("""
    Soil pH refers to how acidic or alkaline your soil is. It directly affects the nutrients available to your plants. By knowing your soil's pH, you can make informed decisions about amending your soil to create the perfect environment for your plants to flourish.
    """)
    st.markdown("""
    Here are the soil types we can identify:
    - Alluvial soil
    - Black soil
    - Clay soil
    - Red soil
    """)
#     sample_images = {
#        "Sample Image 1": "./Pictures/soil nutrition/1000_F_240425429_YL91trtDxXQl8L0OKP7zyngeSb63olAC.jpg",
#        "Sample Image 2": "./Pictures/soil nutrition/Black_1.jpg",
#        "Sample Image 3": "./Pictures/soil nutrition/Clay_1.jpg",
#        "Sample Image 4": "./Pictures/soil nutrition/Copy of image5.jpeg",
#        "Sample Image 5": "./Pictures/soil nutrition/Copy of download (1).jpg",
#        "Sample Image 6": "./Pictures/soil nutrition/Clay_12.jpg",
#    }

    # selected_sample = st.selectbox("select a sample image", options=list(sample_images.keys()))
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    image = None
    # if selected_sample:
    #     image_path = sample_images[selected_sample]
    #     image = Image.open(image_path)
        
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        processor, model = load_model("Soil Nutrition")
        predicted_pH, predicted_soil_type, confidence = apply_scanning_effect_and_process(image, predict_soil_nutrition, model)
        
        st.image(image, caption='Uploaded Image', width=350 )
        st.subheader("Soil Analysis Results:")
        st.write(f"Predicted pH: {predicted_pH:.2f}")
        st.write(f"Predicted Soil Type: {predicted_soil_type}")
        st.write(f"Confidence: {confidence:.2%}")
        st.write(f"Distribution: {crops[predicted_soil_type]['Distribution']}")
        st.write(f"Characteristics: {crops[predicted_soil_type]['Characteristics']}")
        st.write(f"Suggested crops: {', '.join(crops[predicted_soil_type]['Suitable Crops'])}")
        st.write(f"Chemical Properties: {crops[predicted_soil_type]['Chemical Properties']}")
        st.write(f"Color and Texture: {crops[predicted_soil_type]['Color and Texture']}")
    elif image:
        processor, model = load_model("Soil Nutrition")
        predicted_pH, predicted_soil_type, confidence = apply_scanning_effect_and_process(image, predict_soil_nutrition, model)
        
        st.image(image, caption='Uploaded Image', width=300)
        st.subheader("Soil Analysis Results:")
        st.write(f"Predicted pH: {predicted_pH:.2f}")
        st.write(f"Predicted Soil Type: {predicted_soil_type}")
        st.write(f"Confidence: {confidence:.2%}")
        st.write(f"Distribution: {crops[predicted_soil_type]['Distribution']}")
        st.write(f"Characteristics: {crops[predicted_soil_type]['Characteristics']}")
        st.write(f"Suggested crops: {', '.join(crops[predicted_soil_type]['Suitable Crops'])}")
        st.write(f"Chemical Properties: {crops[predicted_soil_type]['Chemical Properties']}")
        st.write(f"Color and Texture: {crops[predicted_soil_type]['Color and Texture']}")
        

# Plant Disease page content
def plant_disease_page():
    st.title("Spot Plant Problems Early: Be Your Plant's Hero!")
    st.header("Diagnose Your Plant's Woes Now!")
    st.markdown("""
    Catching plant diseases early is crucial for saving your precious crops. Our "Plant Disease Identification" feature acts as your personal plant doctor!
    """)
    st.markdown("""
    Simply upload a picture of your ailing plant, and our app will leverage image recognition technology to identify various diseases affecting a wide range of plants.
    """)
    st.markdown("""
    With a clear diagnosis, you can take swift action to treat the problem and protect your harvest. Our app provides information on common treatment options for each identified disease.
    """)
#     sample_images = {
#        "Sample Image 1": "./Pictures/plantdisease/pepperbellhealthu.jpeg",
#        "Sample Image 2": "./Pictures/plantdisease/plant.jpeg",
#        "Sample Image 3": "./Pictures/plantdisease/potatolateblight.jpeg",
#    }

    # selected_sample = st.selectbox("select a sample image", options=list(sample_images.keys()))
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    image = None
    # if selected_sample:
    #     image_path = sample_images[selected_sample]
    #     image = Image.open(image_path)
        
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        processor, model = load_model("Plant disease")
        labels = labels_dict["Plant disease"]
        result, confidence = apply_scanning_effect_and_process(image, predict_other_with_confidence, processor, model, labels)
        
        st.image(image, caption='Uploaded Image', width=300)
        st.subheader("Disease Analysis Results:")
        st.write(f"Detected Disease: {result}")
        st.write(f"Confidence: {confidence:.2%}")
        disease_data = disease_info[result]
        for key, value in disease_data.items():
            st.write(f"{key}: {value}")
    elif image:
        processor, model = load_model("Plant disease")
        labels = labels_dict["Plant disease"]
        result, confidence = apply_scanning_effect_and_process(image, predict_other_with_confidence, processor, model, labels)
        
        st.image(image, caption='Uploaded Image', width=300)
        st.subheader("Disease Analysis Results:")
        st.write(f"Detected Disease: {result}")
        st.write(f"Confidence: {confidence:.2%}")
        disease_data = disease_info[result]
        for key, value in disease_data.items():
            st.write(f"{key}: {value}")

# Cotton Pests page content
def cotton_pests_page():
    st.title('Protect Your Cotton Crop: Identify Pests Before They Cause Havoc!')
    st.header('Identify Cotton Pests in Your Field Now!')
    st.markdown("""
    Cotton farmers face unique challenges when it comes to protecting their crops from destructive pests. Our "Cotton Pest Identification" feature is here to help!
    """)
    st.markdown("""
    Using powerful image recognition, our app can identify common cotton pests like cotton aphids, bollworms,thrips,whiteflies and red cotton bugs from a simple picture.
    """)
    st.markdown("""
    By equipping you with this knowledge, you can take appropriate measures to control pest populations and ensure a healthy, high-yielding cotton harvest. 
    """)
#     sample_images = {
#     "Sample Image 1": "./Pictures/cotton pest/download (1).jpeg",  # This one already has forward slashes
#     "Sample Image 2": "./Pictures/cotton pest/download (7).jpeg",
#     "Sample Image 3": "./Pictures/cotton pest/B2650093-Cotton_aphids (1).jpg",
#     "Sample Image 4": "./Pictures/cotton pest/download (4).jpeg",  # Added missing image entry
#     "Sample Image 5": "./Pictures/cotton pest/download (6).jpeg",  # Added missing image entry
#     "Sample Image 6": "./Pictures/cotton pest/Pink/download (4).jpeg",  # Added missing image entry
#     "Sample Image 7": "./Pictures/cotton pest/erias-vitella-300x161.jpg",
# }

    # selected_sample = st.selectbox("select a sample image", options=list(sample_images.keys()))
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    image = None
    # if selected_sample:
    #     image_path = sample_images[selected_sample]
    #     image = Image.open(image_path)
    
    if uploaded_file is not None or image:
        if uploaded_file:
            image = Image.open(uploaded_file)
        
        processor, model = load_model("Cotton Pests")
        labels = labels_dict["Cotton Pests"]
        result, confidence = apply_scanning_effect_and_process(image, predict_other_with_confidence, processor, model, labels)
        
        st.image(image, caption='Analyzed Image', width=300)
        st.subheader(f"Detected Pest: {result}")
        st.write(f"Confidence: {confidence:.2%}")
        pest_data = pest_info[result]
        for key, value in pest_data.items():
            st.write(f"**{key}:** {value}")
        

            
def mango_ripeness_page():
    st.title('Mango Magic: Unlocking Flavor with Ripeness Detection')
    st.header('Upload an Image for Ripeness Detection')
    st.markdown("""
   Picking a perfectly ripe mango can be tricky. But worry no more! Our user-friendly tool takes the guesswork out of mango selection. Upload an image of your mango, and we'll analyze its visual characteristics to determine its ripeness stage.
""")
    st.markdown("""
    Our system identifies mangoes based on the following categories:""") 
    st.markdown("""
        Ripe: These mangoes have a slight give when pressed gently, a sweet fragrance, and a vibrant yellow or orange color (depending on the variety). They're perfect for eating fresh or using in desserts.""")
    st.markdown("""
        Partially Ripe: These mangoes may still be slightly firm, but should have a hint of give. Their color might be a mix of green and yellow/orange. They can be left at room temperature to ripen further or enjoyed in salads or chutneys.""")
    st.markdown("""
        Unripe: These mangoes are mostly green and firm to the touch. They're not quite ready for eating yet, but can be used for pickling or chutneys.""")
    st.markdown("""
        Early Ripe: These mangoes may have some yellow or orange patches, but might still be too firm and lack the characteristic sweetness. It's best to let them ripen further at room temperature.""")
    st.markdown("""
        With our tool, you can confidently choose mangoes that are perfectly ripe and ready to savor!
        """
    )
   
#     sample_images = {
#     "Sample Image 1": "./Pictures/mango page/bunch-green-yellow-ripe-mango-tree-garden-selective-focus-50923505.jpg",
#     "Sample Image 2": "./Pictures/mango page/55N6BQ5DIVXIMKNI5KZ54BGEFY.jpg",
#     "Sample Image 3": "./Pictures/mango page/closeup-ripe-mango-fruits-on-tree-scientific-name-mangifera-indica-CN80XF.jpg",
#     "Sample Image 4": "./Pictures/mango page/images (3).jpeg",
#     "Sample Image 5": "./Pictures/mango page/stock-photo-vibrant-unripe-mango-fruits-hanging-from-a-healthy-tree-branch-2339198257.jpg"
# }

    # selected_sample = st.selectbox("select a sample image", options=list(sample_images.keys()))
    image = None
    # if selected_sample:
    #     image_path = sample_images[selected_sample]
    #     image = Image.open(image_path)
            
    uploaded_file = st.file_uploader("Or upload your own image", type=["jpg", "jpeg", "png"])

    use_webcam = st.checkbox("Use webcam")

        # Initialize session state for capturing image
    if "capture" not in st.session_state:
        st.session_state.capture = False

    ctx = None
    if use_webcam:
        ctx = webrtc_streamer(
            key="webcam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessor,
            rtc_configuration={
                    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                },
            media_stream_constraints={"video": True, "audio": False},
            )

    if ctx and ctx.video_processor:
        if st.button("Capture Photo"):
            st.session_state.capture = True
        
        if st.session_state.capture and ctx.video_processor.frame is not None:
            frame = ctx.video_processor.frame
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            st.session_state.capture = False

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

    if image:
        conf_threshold = st.slider('Confidence Threshold', 0.0, 1.0, 0.25)
        iou_threshold = st.slider('IoU Threshold', 0.0, 1.0, 0.45)

        _, model = load_model("mango")
        result_image, detected_objects = apply_scanning_effect_and_process(image, predict_yolo, model, conf_threshold, iou_threshold)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption='Original Image', width=300)
        with col2:
            st.image(result_image, caption='YOLO Result', width=300)
        
        df_summary = summarize_detections(detected_objects)
        plot_detection_summary(df_summary)
        
        st.subheader("Detailed Detections:")
        st.dataframe(df_summary)


# Fruit Ripeness page content
def fruit_ripeness_page():
    st.title('Know Your Tomatoes')
    st.header('Upload an Image for Ripeness Detection')
    st.markdown("""
    Ever unsure if the tomato at the store is at its peak ripeness? Wondering if your homegrown tomatoes are ready to be picked? Fear not! Our AI-powered tool takes the mystery out of tomato freshness. Simply upload an image of your tomato, and we'll analyze its color, texture, and other visual cues to determine its ripeness stage.
""")
    st.markdown("""
    Our system identifies tomatoes based on the following categories:""") 
    st.markdown("""
        Tomato Ripe: These tomatoes have a vibrant red color, a slightly soft but firm texture, and no blemishes. They're perfect for salads, sandwiches, or enjoying on their own.""")
    st.markdown("""
        Tomato Half-Ripe: These tomatoes are starting to turn red, but may still have some green patches. They're ideal for those who prefer a slightly tart flavor in their tomatoes.""")
    st.markdown("""
        Tomato Unripe: These tomatoes are mostly green, with perhaps a hint of red starting to show. They're not quite ready for eating yet, but can be used for cooking or pickling.""")
    st.markdown("""
        Tomato Overripe: These tomatoes are a deep red color, may be mushy to the touch, and might have some wrinkles or cracks. While still edible, they're best suited for sauces, soups, or stews.""")
    st.markdown("""
        Tomato Rotten: These tomatoes should be avoided. They'll be very soft, mushy, and may have visible mold or discoloration.
   """)
    st.markdown("""
        Let our tool be your guide to enjoying tomatoes at their finest!
        """
    )
   
#     sample_images = {
#     "Sample Image 1": "./Pictures/fruit ripeness or tomato page/Red-Ripe-Tomatoes-on-Vine.jpg",
#     "Sample Image 2": "./Pictures/fruit ripeness or tomato page/tomato blight.jpg",
#     "Sample Image 3": "./Pictures/fruit ripeness or tomato page/rotten tomato.jpeg",
#     "Sample Image 4": "./Pictures/fruit ripeness or tomato page/ripening-tomatoes-at-home.jpg"
# }

    # selected_sample = st.selectbox("select a sample image", options=list(sample_images.keys()))
    image = None
    # if selected_sample:
    #     image_path = sample_images[selected_sample]
    #     image = Image.open(image_path)
            
    uploaded_file = st.file_uploader("Or upload your own image", type=["jpg", "jpeg", "png"])

    use_webcam = st.checkbox("Use webcam")

        # Initialize session state for capturing image
    if "capture" not in st.session_state:
        st.session_state.capture = False

    ctx = None
    if use_webcam:
        ctx = webrtc_streamer(
            key="webcam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessor,
            rtc_configuration={
                    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                },
            media_stream_constraints={"video": True, "audio": False},
            )

    if ctx and ctx.video_processor:
        if st.button("Capture Photo"):
            st.session_state.capture = True
        
        if st.session_state.capture and ctx.video_processor.frame is not None:
            frame = ctx.video_processor.frame
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            st.session_state.capture = False

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

    if image:
        conf_threshold = st.slider('Confidence Threshold', 0.0, 1.0, 0.25)
        iou_threshold = st.slider('IoU Threshold', 0.0, 1.0, 0.45)

        _, model = load_model("Fruit Ripeness")
        result_image, detected_objects = apply_scanning_effect_and_process(image, predict_yolo, model, conf_threshold, iou_threshold)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption='Original Image', width=300)
        with col2:
            st.image(result_image, caption='YOLO Result', width=300)
        
        df_summary = summarize_detections(detected_objects)
        plot_detection_summary(df_summary)
        
        st.subheader("Detailed Detections:")
        st.dataframe(df_summary)


        
        
            

# YOLO Object Detection page content
def yolo_page():
    st.title('Pick Bananas at Their Peak: Savor the Perfect Flavor!')
    st.header('Find Out When Your Bananas Are Ready to Pick!')
    st.markdown("""
    Our Object Detection model powered by YOLO can identify and locate objects within an image. You can adjust the confidence and IoU thresholds to fine-tune the detection results.
    """)
    st.markdown("""
   Knowing exactly when to pick your bananas can be tricky. Our "Fruit Ripeness Detection" feature takes the guesswork out of banana harvesting.
    """)
    st.markdown("""
    Simply upload a picture of your banana bunch, and our app will analyze the image using the YOLO object detection model.
    """)
    st.markdown("""
    Here are the classes and how it works:
    """)
    st.markdown("""
    **Fresh Ripe Banana (0):** The model identifies a banana as fresh ripe when it detects a predominantly yellow peel with minimal blemishes or spots. There might be a slight hint of green at the stem end, indicating recent growth.
    """)
    st.markdown("""
    **Fresh Unripe Banana (1):** The model classifies a banana as fresh unripe when the peel appears predominantly green with no signs of yellowing. The stem end might be a vibrant green, suggesting the banana is still maturing on the plant.
    """)
    
    st.markdown("""
    **Overripe Banana (2):** An overripe banana will be recognized by the model when the peel exhibits extensive browning and wrinkling. The overall color may be a deep yellow with significant dark spots scattered across the surface.
    """)
    
    st.markdown("""
    **Ripe Banana (3):** This category might be used if the model struggles to definitively differentiate between a fresh ripe and a ripe banana. The peel could be a uniform yellow with minimal browning or blemishes.
    """)
    
    st.markdown("""
   **Rotten Banana (4):** The model identifies a rotten banana when the peel displays a significant amount of blackening and mushy texture. There might be mold present or even leakage of liquid from the banana.
    """)
    
    st.markdown("""
   **Unripe Banana (5):** Similar to the fresh unripe category, this classification might be used for bananas with a predominantly green peel but with a slight hint of yellow at the tip, indicating the very early stages of ripening.
    """)
    

#     sample_images = {
#        "Sample Image 1": "./Pictures/yolo or banana page/banana.jpeg",
#        "Sample Image 2": "./Pictures/yolo or banana page/1-banana-ripening-sequence-ted-kinsman.jpg",
#        "Sample Image 3": "./Pictures/yolo or banana page/download (1).jpeg",
#    }

    # selected_sample = st.selectbox("select a sample image", options=list(sample_images.keys()))
    image = None
    # if selected_sample:
    #     image_path = sample_images[selected_sample]
    #     image = Image.open(image_path)
        
    uploaded_file = st.file_uploader("Or upload your own image", type=["jpg", "jpeg", "png"])

    use_webcam = st.checkbox("Use webcam")

    # Initialize session state for capturing image
    if "capture" not in st.session_state:
        st.session_state.capture = False

    ctx = None
    if use_webcam:
        ctx = webrtc_streamer(
            key="webcam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessor,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"video": True, "audio": False},
        )

    if ctx and ctx.video_processor:
        if st.button("Capture Photo"):
            st.session_state.capture = True
        
        if st.session_state.capture and ctx.video_processor.frame is not None:
            frame = ctx.video_processor.frame
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            st.session_state.capture = False

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

    if image:
        conf_threshold = st.slider('Confidence Threshold', 0.0, 1.0, 0.25)
        iou_threshold = st.slider('IoU Threshold', 0.0, 1.0, 0.45)

        _, model = load_model("YOLO")
        result_image, detected_objects = apply_scanning_effect_and_process(image, predict_yolo, model, conf_threshold, iou_threshold)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption='Original Image', width=300)
        with col2:
            st.image(result_image, caption='YOLO Result', width=300)
        
        df_summary = summarize_detections(detected_objects)
        plot_detection_summary(df_summary)
        
        st.subheader("Detailed Detections:")
        st.dataframe(df_summary)



# Labels dictionary
labels_dict = {
    "Plant disease": [
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
        'Blueberry___healthy', 'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
        'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
        'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
        'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
        'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
        'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
        'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
        'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
        'Tomato___healthy'
    ],
    "Cotton Pests": [
        "American Bollworm", "Cotton Aphid", "Pink Bollworm", "Red Cotton Bug",
        "Spotted Bollworm", "Thrips", "Whitefly"
    ],
    "Fruit Ripeness": [
        "FreshApple", "FreshBanana", "FreshGrape", "FreshGuava", "FreshJujube",
        "FreshOrange", "FreshPomegranate", "FreshStrawberry", "RottenApple",
        "RottenBanana", "RottenGrape", "RottenGuava", "RottenJujube",
        "RottenOrange", "RottenPomegranate", "RottenStrawberry"
    ],
    "Soil Nutrition": [
        'Alluvial soil', 'Black soil', 'Clay soil', 'Red soil'
    ]
}

# Main Streamlit app
def main():
    init_session_state()
    
    if st.session_state['authentication_status']:
        main_app()
    else:
        login_page()

if __name__ == "__main__":
    main()