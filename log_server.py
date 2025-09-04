from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import os
import threading

LOG_FILE_PATH = "/root/V2IpLimit/connections_log.txt"
CACHE_FILE_PATH = "/root/V2IpLimit/cache_logs.txt"

app = FastAPI()


cached_logs = []

def load_cached_logs():
    global cached_logs
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as cache_file:
            cached_logs = [line.strip() for line in cache_file.readlines()]


def reset_cache():
    global cached_logs
    cached_logs = []
    with open(CACHE_FILE_PATH, "w", encoding="utf-8") as cache_file:
        cache_file.write("")  


def save_to_cache(log_line):
    with open(CACHE_FILE_PATH, "a", encoding="utf-8") as cache_file:
        cache_file.write(log_line + "\n")

def auto_update_cache():
    global cached_logs
    last_size = os.path.getsize(LOG_FILE_PATH) if os.path.exists(LOG_FILE_PATH) else 0

    while True:
        try:
            asyncio.run(asyncio.sleep(2)) 

            if os.path.exists(LOG_FILE_PATH):
                new_size = os.path.getsize(LOG_FILE_PATH)

                if new_size == 0:
                    print("?? Log file is empty! Resetting cache...")
                    reset_cache()
                    last_size = 0
                    continue

                if new_size > last_size:  
                    with open(LOG_FILE_PATH, "r", encoding="utf-8") as file:
                        file.seek(last_size)
                        new_lines = file.read().splitlines()
                        last_size = new_size

                        for line in new_lines:
                            line = line.strip()
                            cached_logs.append(line)
                            save_to_cache(line) 
            print(f"?? Error in cache update: {e}")


cache_thread = threading.Thread(target=auto_update_cache, daemon=True)
cache_thread.start()

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Logs</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css">
    <style>
        body { background-color: #f8f9fa; font-family: Arial, sans-serif; }
        .container { margin-top: 20px; }
        .table-container { max-height: 500px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="text-center">?? Live Logs</h2>
        <div class="table-container">
            <table id="logTable" class="table table-striped">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>User Email</th>
                        <th>Destination</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <script>
        $(document).ready(function() {
            let logTable = $("#logTable").DataTable({
                "pageLength": 50,
                "order": [[0, "desc"]]
            });

            let ws = new WebSocket("ws://" + window.location.host + "/ws");

            ws.onmessage = function(event) {
                let logData = JSON.parse(event.data);
                logTable.row.add([logData.time, logData.email, logData.destination]).draw(false);
            };
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get():
    return html

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global cached_logs
    await websocket.accept()

  
    for line in cached_logs:
        parts = line.split(" - ")
        if len(parts) == 2 and " connected to " in parts[1]:
            time, info = parts
            email, destination = info.split(" connected to ")
            await websocket.send_json({"time": time.strip(), "email": email.strip(), "destination": destination.strip()})

    last_size = os.path.getsize(LOG_FILE_PATH)

    while True:
        await asyncio.sleep(1)

        if os.path.exists(LOG_FILE_PATH):
            new_size = os.path.getsize(LOG_FILE_PATH)


            if new_size == 0:
                print("?? Log file was cleared! Resetting cache...")
                reset_cache()
                last_size = 0
                continue

            if new_size > last_size:
                with open(LOG_FILE_PATH, "r", encoding="utf-8") as file:
                    file.seek(last_size)
                    new_lines = file.readlines()
                    last_size = new_size

                    for line in new_lines:
                        line = line.strip()
                        cached_logs.append(line)  

                        parts = line.split(" - ")
                        if len(parts) == 2 and " connected to " in parts[1]:
                            time, info = parts
                            email, destination = info.split(" connected to ")
                            await websocket.send_json({"time": time.strip(), "email": email.strip(), "destination": destination.strip()})

if __name__ == "__main__":
    load_cached_logs() 
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2222)
