import socketio
import os
import zipfile
import io
import base64
import shutil  # <-- needed to delete old project folder

sio = socketio.Client()

url = "https://dev-api-ydfg.onrender.com"

# Event handler for successful connection
@sio.event
def connect():
    print("✅ Client connected to server.") 
    sio.emit('sup', {"msg": "its working?"})

# Event handler for disconnection
@sio.event
def disconnect():
    print("❌ Client disconnected from server.")

# Listen for "working" event
@sio.on('working')
def working(data):
    if data:
        msg = data["msg"]
        print("📩 Received:", msg)
        print("  Project Maker")
        print("\n   1. APK Project")
        print("\n  2. Flask Web App Project")
        print("\n  3. javascript Web App Project")
        print("\n  Due to privacy, you are required to install requirements yourself by running `pip install -r requirements.txt`")
        start = input("\n pick an option:  ")
        if start == "2":
            print("Loading packages....")
            sio.emit("flask_app")
            
        elif start == "1":
            print("Loading packages....")
            sio.emit("apk_app")
        elif start == "3":
            print("Loading packages....")
            sio.emit("js_app")

@sio.on('saved_flask_app')
def saved_flask_app(data):
    if data:
        msg = data["msg"]
        project_dir = data["project_dir"]   # e.g. "flask_app"
        zip_b64 = data["zip_file"]

        print(f"\n{msg}")

        # Decode the zip file
        zip_bytes = base64.b64decode(zip_b64)

        # Where to save the project
        base_dir = "Project_maker"
        target_dir = os.path.join(base_dir, project_dir)

        # Ensure Project_maker exists
        os.makedirs(base_dir, exist_ok=True)

        # 🚨 If target already exists, remove it first
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        # Extract zip directly into Project_maker/project_dir
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            zf.extractall(target_dir)

        print(f"✅ Project saved fresh to {target_dir}")
    else:
        print("No data received")
        
@sio.on('saved_js_app')
def saved_js_app(data):
    if data:
        msg = data["msg"]
        project_dir = data["project_dir"]   # e.g. "flask_app"
        zip_b64 = data["zip_file"]

        print(f"\n{msg}")

        # Decode the zip file
        zip_bytes = base64.b64decode(zip_b64)

        # Where to save the project
        base_dir = "Project_maker"
        target_dir = os.path.join(base_dir, project_dir)

        # Ensure Project_maker exists
        os.makedirs(base_dir, exist_ok=True)

        # 🚨 If target already exists, remove it first
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        # Extract zip directly into Project_maker/project_dir
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            zf.extractall(target_dir)

        print(f"✅ Project saved fresh to {target_dir}")
    else:
        print("No data received")
        
@sio.on('saved_apk')
def saved_apk(data):
    if data:
        msg = data["msg"]
        project_dir = data["project_dir"]   # e.g. "flask_app"
        zip_b64 = data["zip_file"]

        print(f"\n{msg}")

        # Decode the zip file
        zip_bytes = base64.b64decode(zip_b64)

        # Where to save the project
        base_dir = "Project_maker"
        target_dir = os.path.join(base_dir, project_dir)

        # Ensure Project_maker exists
        os.makedirs(base_dir, exist_ok=True)

        # 🚨 If target already exists, remove it first
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        # Extract zip directly into Project_maker/project_dir
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            zf.extractall(target_dir)

        print(f"✅ Project saved fresh to {target_dir}")
    else:
        print("No data received")

# Attempt to connect with auth token
sio.connect(url, auth={"token": "my_secret_token"})

# Keep the client alive
sio.wait()