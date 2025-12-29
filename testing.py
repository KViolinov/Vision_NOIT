# import spotipy
# import requests
# from PIL import Image
# from io import BytesIO
# import numpy as np
# import time
#
# from api_keys.api_keys import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
#
# client_id = SPOTIFY_CLIENT_ID
# client_secret = SPOTIFY_CLIENT_SECRET
#
# sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
#     client_id=client_id,
#     client_secret=client_secret,
#     redirect_uri='http://localhost:8888/callback',
#     scope="user-read-playback-state user-read-currently-playing"))  # Necessary permissions
#
#
# def get_current_song():
#     """Fetches the currently playing song and album cover URL."""
#     track = sp.current_playback()
#     if track and track.get('item'):
#         song_name = track['item']['name']
#         artist_name = track['item']['artists'][0]['name']
#         album_cover_url = track['item']['album']['images'][0]['url']  # Get the largest image
#         return song_name, artist_name, album_cover_url
#     return None, None, None
#
#
# def get_average_color(image_url):
#     """Downloads the image and calculates the average color."""
#     response = requests.get(image_url)
#     image = Image.open(BytesIO(response.content))
#     image = image.resize((50, 50))  # Reduce resolution for faster processing
#     np_image = np.array(image)
#
#     avg_color = np_image.mean(axis=(0, 1))  # Compute mean RGB values
#     return tuple(map(int, avg_color[:3]))  # Convert to integer RGB format
#
#
# def set_color(red, green, blue):
#     """Set the color using RGB values."""
#     url = "http://192.168.10.211/json/state"
#     data = {
#         "on": True,
#         "bri": 255,  # Optional: brightness
#         "seg": [{
#             "col": [[red, green, blue]]
#         }]
#     }
#     response = requests.post(url, json=data)
#     if response.status_code == 200:
#         print(f"✅ LED Color Set: RGB({red}, {green}, {blue})")
#     else:
#         print("⚠️ Failed to update LED color!")
#
#
# last_song = None
#
# while True:
#     song_name, artist_name, cover_url = get_current_song()
#
#     if song_name and song_name != last_song:  # Check if the song has changed
#         last_song = song_name
#         avg_color = get_average_color(cover_url)
#
#         print(f"🎵 Now Playing: {song_name} - {artist_name}")
#         print(f"🎨 Average Album Cover Color (RGB): {avg_color}")
#
#         # Set the LED color to match the album cover
#         set_color(*avg_color)
#
#     time.sleep(5)  # Wait for 5 seconds before checking again
#
from jarvis_functions.essential_functions.contact_locator import find_contact

# from jarvis_functions.send_message_instagram.input_to_message_ai import *
#
# text = "Искам да пратиш съобщение на Мерт, че е тъп турчин и ще му избием зъбите"
# #text = "Искам да пратиш съобщение към Вероника, и я питай какво прави"
#
# generate_message(text)


# from ui.vision_ui import VisionAPI
# import webview
# import threading
# import time
#
# def simulate_behavior(api):
#     """Runs in a background thread."""
#     while True:
#         time.sleep(5)
#         api.set_state("thinking")
#         time.sleep(5)
#         api.set_state("answering")
#         time.sleep(5)
#         api.set_state("idle")
#
# if __name__ == "__main__":
#     api = VisionAPI()
#     window = webview.create_window("Vision Interface MK4", "ui/index.html", js_api=api, width=1920, height=1080)
#     api.window = window
#
#     # Start background behavior in a separate thread
#     threading.Thread(target=simulate_behavior, args=(api,), daemon=True).start()
#
#     # Start the WebView on the main thread
#     webview.start()


# def check_payment(func):
#     def wrapper():
#         print("Before the function call")
#         func()
#         print("After the function call")
#     return wrapper
#
# @check_payment
# def say_hello():
#     print("Hello, World!")
#
# say_hello()


# from jarvis_functions.essential_functions.contact_locator import find_contact
#
# print(find_contact("тати"))
# print(find_contact("Вероника", field="имейл"))

# import requests
#
# url = "http://kvb-bg.com/Vision/api/login_api.php"
# payload = {
#     "email": "konstantinviolinov@outlook.com",
#     "password": "kv0889909595"
# }
#
# res = requests.post(url, json=payload, timeout=10)
#
# print("Status code:", res.status_code)
# print("Response headers:", res.headers)
# print("Raw response text:\n", res.text)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import threading
# import time
# import requests
# import socket
#
# app = Flask(__name__)
# CORS(app)
#
# # Store connected clients
# connected_clients = {}
#
#
# def get_local_ip():
#     """Get the local IP address of the computer"""
#     try:
#         # Connect to a remote address to determine the local IP
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.connect(("8.8.8.8", 80))
#             return s.getsockname()[0]
#     except:
#         return "127.0.0.1"
#
#
# @app.route('/register', methods=['POST'])
# def register_client():
#     try:
#         data = request.json
#         client_id = data.get('clientId')
#         ip_address = request.remote_addr
#
#         connected_clients[client_id] = {
#             'ip': ip_address,
#             'last_seen': time.time(),
#             'registered_at': time.time()
#         }
#
#         print(f"📱 Client registered: {client_id} from {ip_address}")
#         print(f"📍 Total connected clients: {len(connected_clients)}")
#
#         return jsonify({'status': 'registered'})
#     except Exception as e:
#         print(f"❌ Registration error: {e}")
#         return jsonify({'error': 'Registration failed'}), 500
#
#
# @app.route('/send-command', methods=['POST'])
# def send_command_to_client():
#     data = request.json
#     client_id = data.get('clientId')
#     command = data.get('command')
#
#     if not client_id or not command:
#         return jsonify({'error': 'Missing clientId or command'}), 400
#
#     if client_id in connected_clients:
#         connected_clients[client_id]['last_command'] = {
#             'command': command,
#             'timestamp': time.time(),
#             'id': f"cmd_{int(time.time())}"
#         }
#
#         print(f"📤 Command sent to {client_id}: '{command}'")
#         return jsonify({
#             'status': 'command_sent',
#             'command': command,
#             'clientId': client_id
#         })
#     else:
#         print(f"❌ Client not found: {client_id}")
#         return jsonify({'error': 'Client not found'}), 404
#
#
# @app.route('/get-command/<client_id>', methods=['GET'])
# def get_command(client_id):
#     if client_id in connected_clients:
#         client_data = connected_clients[client_id]
#         client_data['last_seen'] = time.time()  # Update last seen
#
#         last_command = client_data.get('last_command')
#
#         if last_command:
#             # Clear the command after reading
#             del client_data['last_command']
#             return jsonify({'command': last_command})
#         else:
#             return jsonify({'command': None})
#     else:
#         return jsonify({'error': 'Client not found'}), 404
#
#
# @app.route('/clients', methods=['GET'])
# def list_clients():
#     client_list = {
#         client_id: {
#             'ip': data['ip'],
#             'connected_for': int(time.time() - data['registered_at']),
#             'last_command': data.get('last_command')
#         }
#         for client_id, data in connected_clients.items()
#     }
#     return jsonify({'clients': client_list})
#
#
# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({'status': 'healthy', 'clients_count': len(connected_clients)})
#
#
# def interactive_shell():
#     """Interactive shell to send commands to connected clients"""
#     time.sleep(2)
#     local_ip = get_local_ip()
#     print("\n" + "=" * 60)
#     print("🎮 INTERACTIVE COMMAND SHELL")
#     print("=" * 60)
#     print(f"📍 Server running on: http://{local_ip}:5000")
#     print("📱 Make sure your phone is on the same WiFi network!")
#     print("=" * 60)
#     print("Type commands in format: [client_id] [command]")
#     print("Example: 'mobile-123 call john'")
#     print("Type 'list' to see connected clients")
#     print("Type 'quit' to exit")
#     print("=" * 60)
#
#     while True:
#         try:
#             user_input = input("\n>>> ").strip()
#
#             if user_input.lower() == 'quit':
#                 break
#             elif user_input.lower() == 'list':
#                 print("\n📋 Connected Clients:")
#                 if connected_clients:
#                     for client_id, data in connected_clients.items():
#                         print(f"  • {client_id} ({data['ip']}) - {int(time.time() - data['registered_at'])}s ago")
#                 else:
#                     print("  No clients connected")
#                 continue
#
#             parts = user_input.split(' ', 1)
#             if len(parts) < 2:
#                 print("❌ Invalid format. Use: [client_id] [command]")
#                 continue
#
#             client_id, command = parts
#
#             if client_id not in connected_clients:
#                 print(f"❌ Client '{client_id}' not found. Use 'list' to see connected clients.")
#                 continue
#
#             response = requests.post(
#                 f'http://localhost:5000/send-command',
#                 json={'clientId': client_id, 'command': command}
#             )
#
#             if response.status_code == 200:
#                 print(f"✅ Command sent successfully: '{command}'")
#             else:
#                 print(f"❌ Failed to send command: {response.json().get('error')}")
#
#         except KeyboardInterrupt:
#             break
#         except Exception as e:
#             print(f"❌ Error: {e}")
#
#
# def cleanup_clients():
#     """Remove clients that haven't been seen in 5 minutes"""
#     while True:
#         current_time = time.time()
#         expired_clients = [
#             client_id for client_id, client_data in connected_clients.items()
#             if current_time - client_data['last_seen'] > 300
#         ]
#
#         for client_id in expired_clients:
#             del connected_clients[client_id]
#             print(f"🗑️ Removed expired client: {client_id}")
#
#         time.sleep(60)
#
#
# def auto_broadcast_commands():
#     """Send a command to all connected clients every 20 seconds."""
#     while True:
#         if connected_clients:
#             for client_id in list(connected_clients.keys()):
#                 connected_clients[client_id]['last_command'] = {
#                     'command': 'call 0888503801',
#                     'timestamp': time.time(),
#                     'id': f"cmd_{int(time.time())}"
#                 }
#                 print(f"📤 Auto command sent to {client_id}: call 0889909595")
#         time.sleep(20)  # every 20 seconds
#
#
# if __name__ == '__main__':
#     local_ip = get_local_ip()
#
#     # Start cleanup thread
#     threading.Thread(target=cleanup_clients, daemon=True).start()
#
#     # Start automatic broadcaster
#     threading.Thread(target=auto_broadcast_commands, daemon=True).start()
#
#     print("🚀 Starting Python Server...")
#     print(f"📍 Local URL: http://localhost:5000")
#     print(f"📍 Network URL: http://{local_ip}:5000")
#     print("\n⚠️  Clients will receive 'call 0889909595' every 20 s automatically.\n")
#
#     app.run(host='0.0.0.0', port=5000, debug=True)


import qrcode

img = qrcode.make("Some data here")
type(img)  # qrcode.image.pil.PilImage
img.save("some_file.png")
