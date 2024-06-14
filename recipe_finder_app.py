# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 20:54:17 2024

@author: gowtham.balachan
"""

import streamlit as st
from data_loader import DataLoader
from recipe_matcher import RecipeMatcher
from recipe_generator import RecipeGenerator

class RecipeFinderApp:
    def __init__(self):
        self.data_loader = DataLoader()
        self.df = self.data_loader.load_data('FeedDB.xlsx')
        self.recipe_matcher = RecipeMatcher(self.df)

    def display_recipes(self, ingredients, api_key, chef_role):
        try:
            closest_matches = self.recipe_matcher.get_closest_matches(ingredients)
            recipe_generator = RecipeGenerator(api_key)
            gpt_recipes = recipe_generator.get_recipes_from_gpt(closest_matches, chef_role)

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

def main():
    st.title('Recipe Finder')
    st.write('Enter ingredients to find recipes you can make with them (comma-separated).')
    
    st.sidebar.title('Settings')
    api_key = st.sidebar.text_input('Enter your OpenAI API key:', type='password')

    chef_roles = ['Asian Chef', 'Continental Chef', 'Indian Chef', 'Middle Eastern Chef', 'North American Chef']
    selected_chef_role = st.sidebar.selectbox('Select Chef Role:', chef_roles)

    ingredient_input = st.text_input('Ingredients:', '')

    if st.button('Find Recipes'):
        if ingredient_input:
            if ',' in ingredient_input:
                if api_key:
                    app = RecipeFinderApp()
                    app.display_recipes(ingredient_input, api_key, selected_chef_role)
                else:
                    st.write('Please enter your OpenAI API key.')
            else:
                st.write('Please enter ingredients separated by commas.')
        else:
            st.write('Please enter ingredients.')

if __name__ == '__main__':
    main()
