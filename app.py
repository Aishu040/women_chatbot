from flask import Flask, render_template, request, jsonify
import openai
import sqlite3
import requests  # Import requests library for making HTTP requests to the Node.js server

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'botkey'

# Node.js server URL
node_server_url = 'http://localhost:3001'  # Update with your Node.js server URL

# Create SQLite database and table if not exists
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL
    );
''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_message', methods=['POST'])
def process_message():
    user_message = request.form['user_message']

    # Save the user message to SQLite database
    save_to_database(user_message)

    # Process the user message using GPT-4
    chatbot_response = generate_chatbot_response(user_message)

    return jsonify({'chatbot_response': chatbot_response})

@app.route('/get_prompt', methods=['GET'])
def get_prompt():
    task = request.args.get('task')
    prompt = read_prompt_from_file(task)
    return jsonify({'prompt': prompt})

def save_to_database(user_message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_messages (message) VALUES (?)', (user_message,))
    conn.commit()
    conn.close()

def generate_chatbot_response(user_message):
    # Add organization ID or any other necessary parameters
    organization_id = 'org-Kpm4Woj3aNQsZoESOLciIiT9'

    # Construct the prompt with additional parameters
    prompt = f"Women empowerment chatbot: {user_message}, organization_id={organization_id}"

    # Make a request to the GPT-4 API (Davinci Codex)
    response = requests.post(
        'https://api.openai.com/v1/engines/davinci-codex/completions',
        json={'prompt': prompt, 'max_tokens': 150},
        headers={'Authorization': 'Bearer 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'}
    )

    # Check if the API request was successful
    if response.status_code != 200:
        return 'Error in GPT-4 API response'

    chatbot_response = response.json().get('choices', [{}])[0].get('text', 'Error in GPT-4 response')

    print("GPT-4 API Response:", chatbot_response)

    return chatbot_response

def read_prompt_from_file(task):
    with open('prompt.txt', 'r') as file:
        prompts = dict(map(str.strip, line.split(':', 1)) for line in file)
    return prompts.get(task, 'Invalid task')

if __name__ == '__main__':
    app.run(debug=True)
