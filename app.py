from flask import Flask, render_template, request, jsonify
import http.client
import json
from urllib.parse import quote
from flask import redirect, url_for


app = Flask(__name__)


app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'
RAPIDAPI_KEY = '61c1af29aemsh3760981ad1bf8a6p1ec6b4jsna57898205928'

@app.route('/')
def home():
    # Check if the user is logged in
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend_recipe():
    user_input = request.form['user_input']  

    conn = http.client.HTTPSConnection("spoonacular-recipe-food-nutrition-v1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    api_request_url = f"/recipes/complexSearch?query={quote(user_input)}&number=19"
    
    conn.request("GET", api_request_url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    response_data = data.decode("utf-8")
    recipes = []  # Initialize an empty list to store recipe details
    error_message = None  # Initialize error_message as None
    
    try:
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


@app.route('/random_recipe', methods=['GET'])
def random_recipe():
    conn = http.client.HTTPSConnection("spoonacular-recipe-food-nutrition-v1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    api_request_url = "/recipes/random"

    conn.request("GET", api_request_url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse the response data (JSON)
    response_data = data.decode("utf-8")
    recipe = {}  # Initialize an empty dictionary to store the random recipe details
    error_message = None  # Initialize error_message as None
    
    try:
        # Attempt to parse JSON data
        response_json = json.loads(response_data)
        recipe = response_json['recipes'][0] if 'recipes' in response_json else {}
    except Exception as e:
        error_message = f"Error parsing API response: {e}"
        return render_template('error.html', error_message=error_message)
    
    if not recipe:
        error_message = "No random recipe found."
        return render_template('error.html', error_message=error_message)

    # Get detailed information about the random recipe
    recipe_id = recipe.get('id', 0)
    api_request_url_details = f"/recipes/{recipe_id}/information"
    conn.request("GET", api_request_url_details, headers=headers)
    res_details = conn.getresponse()
    data_details = res_details.read()
    response_data_details = data_details.decode("utf-8")


    recipe_details = {}
    try:
        response_json_details = json.loads(response_data_details)
        recipe_details = response_json_details
    except Exception as e:
        error_message = f"Error parsing recipe details API response: {e}"
        return render_template('error.html', error_message=error_message)

    # Get instructions for the random recipe
    api_request_url_instructions = f"/recipes/{recipe_id}/analyzedInstructions"
    conn.request("GET", api_request_url_instructions, headers=headers)
    res_instructions = conn.getresponse()
    data_instructions = res_instructions.read()
    response_data_instructions = data_instructions.decode("utf-8")

    instructions = []
    try:
        response_json_instructions = json.loads(response_data_instructions)
        if response_json_instructions:
            instructions = response_json_instructions[0].get('steps', [])
    except Exception as e:
        error_message = f"Error parsing instructions API response: {e}"
        return render_template('error.html', error_message=error_message)
    
    ingredients_with_quantities = []
    if 'extendedIngredients' in recipe_details:
        for ingredient in recipe_details['extendedIngredients']:
            name = ingredient.get('original', ingredient.get('name'))
            if name:
                ingredients_with_quantities.append(name)

        
    return render_template('recipe_details.html', recipe_details=recipe_details, instructions=instructions, ingredients_with_quantities=ingredients_with_quantities)

import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

# Initialize SQLite database
conn = sqlite3.connect('user_profiles.db')
c = conn.cursor()

# Create users table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY,
             username TEXT NOT NULL,
             password TEXT NOT NULL,
             email TEXT NOT NULL,
             allergens TEXT
             )''')
conn.commit()

conn = sqlite3.connect('saved_recipes.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS saved_recipes (
             id INTEGER PRIMARY KEY,
             user_id INTEGER NOT NULL,
             recipe_title TEXT NOT NULL,
             recipe_id INTEGER NOT NULL,
             FOREIGN KEY (user_id) REFERENCES users (id)
             )''')
conn.commit()

# Fetch all rows from the saved_recipes table
c.execute("SELECT * FROM saved_recipes")
rows = c.fetchall()

# Print the column names
print("ID\tUser ID\tRecipe title\tRecipe_ID")
print("---------------------------------")

# Print the content of the table
for row in rows:
    recipe_id, user_id, recipe_title, recipe_id = row
    print(f"{recipe_id}\t{user_id}\t{recipe_title}\t{recipe_id}")

# Close the connection
conn.close()


# Close the connection
conn.close()


# Routes for login, registration, profile, and recipe management
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Authenticate user
        if authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', message='Invalid username or password')
    return render_template('login.html', message='')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        allergens = request.form['allergens']
        # Register new user
        if register_user(username, password, email, allergens):
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            return render_template('register.html', message='Username or email already exists')
    return render_template('register.html', message='')

from flask import render_template

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        user_id = get_user_id(username)  # Assuming you have implemented this function
        if user_id is not None:
            saved_recipes = get_saved_recipes(user_id)
            return render_template('profile.html', username=username, saved_recipes=saved_recipes)
        else:
            return render_template('profile.html', username=username, saved_recipes=[])  # No recipes found for the user
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Function to authenticate user
def authenticate_user(username, password):
    conn = sqlite3.connect('user_profiles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return True if user else False

# Function to register new user
def register_user(username, password, email, allergens):
    conn = sqlite3.connect('user_profiles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    user = c.fetchone()
    if user:
        conn.close()
        return False
    else:
        c.execute("INSERT INTO users (username, password, email, allergens) VALUES (?, ?, ?, ?)",
                  (username, password, email, allergens))
        conn.commit()
        conn.close()
        return True

def get_user_id(username):
    try:
        conn = sqlite3.connect('user_profiles.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = c.fetchone()
        if user_id:
            return user_id[0]  # Return the user ID
        else:
            return None  # Return None if the user is not found
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return None
    finally:
        conn.close()


# Function to save user recipe to the database
def save_user_recipe_to_database(user_id, recipe_title, recipe_id):
    conn = sqlite3.connect('saved_recipes.db')
    c = conn.cursor()
    c.execute("INSERT INTO saved_recipes (user_id, recipe_title, recipe_id) VALUES (?, ?, ?)", (user_id, recipe_title, recipe_id))
    conn.commit()
    conn.close()

def get_saved_recipes(user_id):
    try:
        conn = sqlite3.connect('saved_recipes.db')
        c = conn.cursor()
        c.execute("SELECT id, recipe_title FROM saved_recipes WHERE user_id = ?", (user_id,))
        saved_recipes = c.fetchall()
        return saved_recipes
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return []
    finally:
        conn.close()


import logging

@app.route('/save_user_recipe', methods=['POST'])
def save_recipe():
    if 'username' in session:
        username = session['username']
        recipe_title = request.form.get('recipe_title')
        recipe_id = request.form.get('recipe_id')


        if not recipe_title:
            return render_template('error.html', error_message="Recipe name cannot be empty.")
        
        try:
            # Get user ID from the database using the username
            conn = sqlite3.connect('user_profiles.db')
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = c.fetchone()[0]
            
            # Save recipe to the database
            save_user_recipe_to_database(user_id, recipe_title, recipe_id)
            
            # Redirect to the profile page after saving
            return redirect(url_for('profile'))
        except sqlite3.IntegrityError as e:
            logging.error(f"IntegrityError occurred: {str(e)}")
            conn.rollback()  # Rollback the transaction in case of an integrity error
            return render_template('error.html', error_message="Error saving recipe. Please try again.")
        except Exception as e:
            logging.error(f"Database error occurred: {str(e)}")
            conn.rollback()  # Rollback the transaction in case of any other error
            return render_template('error.html', error_message="An error occurred while saving the recipe.")
        finally:
            conn.close()
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
