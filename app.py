from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Virtual Pet Challenge API is running!"

if __name__ == "__main__":
    app.run(debug=True)
