from flask import Flask, render_template, request, jsonify
import http.client
import json
from urllib.parse import quote


app = Flask(__name__)

RAPIDAPI_KEY = '61c1af29aemsh3760981ad1bf8a6p1ec6b4jsna57898205928'

@app.route('/')
def home():
    return render_template('index.html')

    

@app.route('/recommend', methods=['POST'])
def recommend_recipe():
    user_input = request.form['user_input']  

    conn = http.client.HTTPSConnection("spoonacular-recipe-food-nutrition-v1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    api_request_url = f"/recipes/complexSearch?query={quote(user_input)}&number=5"
    
    conn.request("GET", api_request_url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse the response data (JSON)
    response_data = data.decode("utf-8")
    recipes = []  # Initialize an empty list to store recipe details
    error_message = None  # Initialize error_message as None
    
    try:
        # Attempt to parse JSON data
        response_json = json.loads(response_data)
        if 'results' in response_json:
            recipes = response_json['results']
        else:
            error_message = "No recipe recommendations found."
    except Exception as e:
        error_message = f"Error parsing API response: {e}"
        return render_template('index.html', error_message=error_message)
    
    if error_message:
        return render_template('index.html', error_message=error_message)
    else:
        return render_template('recipes.html', recipes=recipes)

@app.route('/recipe_details/<int:recipe_id>')
def recipe_details(recipe_id):
    conn = http.client.HTTPSConnection("spoonacular-recipe-food-nutrition-v1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    # Fetch recipe details
    api_request_url_details = f"/recipes/{recipe_id}/information"
    conn.request("GET", api_request_url_details, headers=headers)
    res_details = conn.getresponse()
    data_details = res_details.read()
    response_data_details = data_details.decode("utf-8")

    recipe_details = {}
    error_message = None

    try:
        response_json_details = json.loads(response_data_details)
        recipe_details = response_json_details
    except Exception as e:
        error_message = f"Error parsing recipe details API response: {e}"
        return render_template('error.html', error_message=error_message)

    # Fetch instructions
    api_request_url_instructions = f"/recipes/{recipe_id}/analyzedInstructions"
    conn.request("GET", api_request_url_instructions, headers=headers)
    res_instructions = conn.getresponse()
    data_instructions = res_instructions.read()
    response_data_instructions = data_instructions.decode("utf-8")

    instructions = []
    try:
        response_json_instructions = json.loads(response_data_instructions)
        if response_json_instructions and 'steps' in response_json_instructions[0]:
            instructions = response_json_instructions[0]['steps']
    except Exception as e:
        error_message = f"Error parsing instructions API response: {e}"
        return render_template('error.html', error_message=error_message)

        # Extract ingredients with quantities from the extendedIngredients field
    ingredients_with_quantities = []
    if 'extendedIngredients' in recipe_details:
        for ingredient in recipe_details['extendedIngredients']:
            name = ingredient.get('original', ingredient.get('name'))
            if name:
                ingredients_with_quantities.append(name)

    return render_template('recipe_details.html', recipe_details=recipe_details, instructions=instructions, ingredients_with_quantities=ingredients_with_quantities)

if __name__ == '__main__':
    app.run(debug=True)
