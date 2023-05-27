import connexion
app = connexion.FlaskApp(__name__)
app.debug = True

app.add_api("api_schema.yml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
