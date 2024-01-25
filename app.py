from flask import Flask, render_template, request, jsonify
import http.client
import json

app = Flask(__name__)

# Replace 'YOUR_RAPIDAPI_KEY' with your actual RapidAPI key
RAPIDAPI_KEY = '61c1af29aemsh3760981ad1bf8a6p1ec6b4jsna57898205928'

# Define routes
@app.route('/')
def home():
    return render_template('index.html')

    
@app.route('/recommend', methods=['POST'])
def recommend_recipe():
    user_input = request.form['user_input']  # Get user input here

    conn = http.client.HTTPSConnection("spoonacular-recipe-food-nutrition-v1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    # Construct the API request URL using user input
    from urllib.parse import quote

    api_request_url = f"/recipes/complexSearch?query={quote(user_input)}&number=5"

    
    conn.request("GET", api_request_url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse the response data (JSON)
    response_data = data.decode("utf-8")
    recipes = []  # Initialize an empty list to store recipe titles
    error_message = None  # Initialize error_message as None
    
    try:
        # Attempt to parse JSON data
        response_json = json.loads(response_data)
        if 'results' in response_json:
            recipes = [recipe['title'] for recipe in response_json['results']]
        else:
            error_message = "No recipe recommendations found."
    except Exception as e:
        error_message = f"Error parsing API response: {e}"
        return render_template('index.html', error_message=error_message)

    
    
    
    if error_message:
        return render_template('index.html', error_message=error_message)
    else:
        return render_template('index.html', recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
