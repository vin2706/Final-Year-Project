from flask import Flask, render_template, request, jsonify
import http.client

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
    api_request_url = f"/recipes/complexSearch?query={user_input}&number=5"
    
    conn.request("GET", api_request_url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse the response data (JSON) and pass it to the template
    recipes = data.decode("utf-8")
    return render_template('index.html', recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
