import os
import ssl
from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

app = Flask(__name__)

# Configuración MQTT desde variables de entorno
MQTT_SERVER = os.environ.get('MQTT_SERVER', 'mosquitto')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 8883))
MQTT_USER = os.environ.get('MQTT_USER', '')
MQTT_PASS = os.environ.get('MQTT_PASS', '')

print(f"Iniciando conexión MQTT a {MQTT_SERVER}:{MQTT_PORT} con usuario '{MQTT_USER}'")

# Configurar cliente MQTT
mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2, "flask_frontend")

if MQTT_USER and MQTT_PASS:
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

try:
    # Usamos TLS permitiendo certificados autofirmados
    mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
    mqtt_client.tls_insecure_set(True)
except Exception as e:
    print(f"Advertencia: No se pudo configurar TLS. {e}")

try:
    mqtt_client.connect(MQTT_SERVER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print("Conexión MQTT iniciada correctamente en segundo plano.")
except Exception as e:
    print(f"Error al conectar con el broker MQTT en {MQTT_SERVER}:{MQTT_PORT} - {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def send_command():
    data = request.json
    mac_id = data.get('mac_id')
    command_type = data.get('command')
    
    if not mac_id or not command_type:
        return jsonify({'status': 'error', 'message': 'Faltan parámetros (mac_id, command)'}), 400
        
    if command_type == 'destello':
        topic = f'{mac_id}/destello'
        payload = '1'
        mqtt_client.publish(topic, payload, qos=1)
        return jsonify({'status': 'success', 'message': f'Comando de destello enviado al nodo {mac_id}'})
        
    elif command_type == 'setpoint':
        setpoint_val = data.get('value')
        if setpoint_val is None:
            return jsonify({'status': 'error', 'message': 'Falta el valor del setpoint'}), 400
            
        topic = f'{mac_id}/setpoint'
        payload = str(setpoint_val)
        mqtt_client.publish(topic, payload, qos=1)
        return jsonify({'status': 'success', 'message': f'Setpoint {setpoint_val} enviado al nodo {mac_id}'})
        
    return jsonify({'status': 'error', 'message': 'Comando desconocido'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
