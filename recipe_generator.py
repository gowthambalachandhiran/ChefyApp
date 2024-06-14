# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 20:53:46 2024

@author: gowtham.balachan
"""

import openai

class RecipeGenerator:
    def __init__(self, api_key):
        openai.api_key = api_key

    def get_recipes_from_gpt(self, records, chef_role):
        prompt = f"As a {chef_role}, find detailed recipes using the following base information:\n\n"
        for _, row in records.iterrows():
            name = row['Name']
            ingredients = row['RecipeIngredientParts']
            instructions = row['RecipeInstructions']
            prompt += f"Recipe Name: {name}\nIngredients: {ingredients}\nInstructions: {instructions}\n\n"
        prompt += "Provide detailed instructions and include image URL if available."
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            raise ValueError(f"Error fetching recipes from GPT: {str(e)}")
