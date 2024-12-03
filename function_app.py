import azure.functions as func
import pyodbc
import logging
import json
import os  # Import os to retrieve environment variables

app = func.FunctionApp()

@app.function_name(name="InsertHealthData")
@app.route(route="insert-data", methods=["POST"])
def insert_data(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Extract data from the JSON payload
        step_count = req_body.get("step_count")
        heart_rate = req_body.get("heart_rate")

        if step_count is None or heart_rate is None:
            logging.warning("Invalid input: Missing step_count or heart_rate.")
            return func.HttpResponse(
                json.dumps({"error": "Invalid input. Both step_count and heart_rate are required."}),
                status_code=400,
                mimetype="application/json"
            )

        logging.info(f"Received data - Step Count: {step_count}, Heart Rate: {heart_rate}")

        # Retrieve connection string from environment variables
        logging.info("Retrieving connection string...")
        connection_string = os.getenv("SQL_CONNECTION_STRING")
        if not connection_string:
            logging.error("SQL_CONNECTION_STRING environment variable not found.")
            return func.HttpResponse(
                json.dumps({"error": "Database connection string not found."}),
                status_code=500,
                mimetype="application/json"
            )

        # Connect to Azure SQL Database
        logging.info("Connecting to Azure SQL...")
        conn = pyodbc.connect(connection_string)
        logging.info("Connection established successfully.")
        cursor = conn.cursor()

        # Insert data into SQL table
        logging.info("Inserting data into the database...")
        cursor.execute(
            "INSERT INTO HealthData (StepCount, HeartRate, Timestamp) VALUES (?, ?, GETDATE())",
            (step_count, heart_rate)
        )
        conn.commit()

        # Close connection
        cursor.close()
        conn.close()
        logging.info("Data insertion completed and connection closed.")

        return func.HttpResponse(
            json.dumps({"message": "Data inserted successfully!"}),
            status_code=200,
            mimetype="application/json"
        )

    except pyodbc.Error as db_err:
        logging.error(f"Database connection error: {db_err}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Database error: {str(db_err)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except json.JSONDecodeError:
        logging.error("Invalid JSON payload.")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON payload."}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "An unexpected error occurred."}),
            status_code=500,
            mimetype="application/json"
        )
