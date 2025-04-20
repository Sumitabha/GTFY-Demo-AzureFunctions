import azure.functions as func
import pyodbc
import os
import logging
import json
from azure.identity import DefaultAzureCredential

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="getAssignmentsList")
def getAssignmentsList(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request to fetch data from Azure SQL')
    try:
        server = os.getenv('DB_SERVER')  # e.g., yourserver.database.windows.net
        database = os.getenv('DB_NAME')
        driver = '{ODBC Driver 17 for SQL Server}'

        # Get access token from Managed Identity
        credential = DefaultAzureCredential()
        token = credential.get_token("https://database.windows.net/.default")
        access_token = token.token.encode('utf-16-le')

        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};Authentication=ActiveDirectoryAccessToken'
        conn = pyodbc.connect(conn_str, attrs_before={1256: access_token})

        cursor = conn.cursor()
        cursor.execute("SELECT TOP 10 * FROM dbo.assignmentList")
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return func.HttpResponse(json.dumps(rows, default=str), status_code=200, mimetype="application/json")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse("Internal Server Error", status_code=500)