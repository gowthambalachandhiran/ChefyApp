# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 19:44:47 2024

@author: gowtham.balachan
"""

import streamlit as st
import pandas as pd
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to load the data from the Excel file
@st.cache_data
def load_data():
    return pd.read_excel('FeedDB.xlsx')

df = load_data()

# Set up the Streamlit interface
st.title('Recipe Finder')
st.write('Enter ingredients to find recipes you can make with them (comma-separated).')

# Create a sidebar for OpenAI API key input and chef role selection
st.sidebar.title('Settings')
api_key = st.sidebar.text_input('Enter your OpenAI API key:', type='password')

chef_roles = ['Asian Chef', 'Continental Chef', 'Indian Chef', 'Middle Eastern Chef', 'North American Chef']
selected_chef_role = st.sidebar.selectbox('Select Chef Role:', chef_roles)

ingredient_input = st.text_input('Ingredients:', '')

# Function to find the closest matches from the dataset
@st.cache_data
def get_closest_matches(ingredient):
    try:
        if 'RecipeIngredientParts' not in df.columns:
            raise ValueError("DataFrame column 'RecipeIngredientParts' not found.")
        
        # Ensure 'RecipeIngredientParts' is converted to string type and handle potential NaNs
        df['RecipeIngredientParts'] = df['RecipeIngredientParts'].astype(str).fillna('')
        
        # Use TfidfVectorizer for more efficient vectorization
        vectorizer = TfidfVectorizer().fit(df['RecipeIngredientParts'])
        
        # Transform the input ingredient
        input_vector = vectorizer.transform([ingredient])
        
        # Compute cosine similarities
        vectors = vectorizer.transform(df['RecipeIngredientParts'])
        cosine_similarities = cosine_similarity(input_vector, vectors).flatten()
        
        # Get indices of top matches
        top_indices = cosine_similarities.argsort()[-3:][::-1]
        
        # Return top matched records
        return df.iloc[top_indices]
    
    except Exception as e:
        raise ValueError(f"Error in vectorization process: {str(e)}")

# Function to find recipes using GPT-4 Turbo API
def get_recipes_from_gpt(records, api_key, chef_role):
    # Set the OpenAI API key
    openai.api_key = api_key
    
    prompt = f"As a {chef_role}, find detailed recipes using the following base information:\n\n"
    
    for _, row in records.iterrows():
        name = row['Name']
        ingredients = row['RecipeIngredientParts']
        instructions = row['RecipeInstructions']
        prompt += f"Recipe Name: {name}\nIngredients: {ingredients}\nInstructions: {instructions}\n\n"
    
    prompt += "Provide detailed instructions and include image URL if available."
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']

# Function to display recipes
def display_recipes(ingredient, api_key, chef_role):
    try:
        closest_matches = get_closest_matches(ingredient)
        
        gpt_recipes = get_recipes_from_gpt(closest_matches, api_key, chef_role)
        
        st.write("**Debug:** API Response")
        st.write(gpt_recipes)
        
        recipes_list = gpt_recipes.strip().split('\n\n')
        for recipe in recipes_list:
            lines = recipe.split('\n')
            if len(lines) >= 4:
                name = lines[0].split(': ')[1] if ': ' in lines[0] else "No name available"
                image = lines[1].split(': ')[1] if ': ' in lines[1] else ""
                ingredients = lines[2].split(': ')[1] if ': ' in lines[2] else "No ingredients available"
                instructions = lines[3].split(': ')[1] if ': ' in lines[3] else "No instructions available"
                
                st.subheader(name)
                if image:
                    try:
                        st.image(image, caption=name)
                    except:
                        st.write("No image to display")
                st.write(f"**Ingredients:** {ingredients}")
                st.write(f"**Instructions:** {instructions}")
            else:
                st.write("Unexpected recipe format:", recipe)
                
        for index, row in closest_matches.iterrows():
            name = row['Name']
            images = row['Images']
            image_urls = images.split(', ') if images else []
            
            st.subheader(name)
            for image_url in image_urls:
                if image_url:
                    try:
                        st.image(image_url, caption=name)
                    except:
                        st.write("No image to display")
    except Exception as e:
        st.write('Error retrieving recipes:', str(e))

# Add submit button to trigger recipe search
if st.button('Find Recipes'):
    if ingredient_input:
        if api_key:
            # Call the function to process the input and display recipes
            display_recipes(ingredient_input, api_key, selected_chef_role)
        else:
            st.write('Please enter your OpenAI API key.')
    else:
        st.write('Please enter ingredients.')