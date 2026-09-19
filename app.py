from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Stream Link API Running'

@app.route('/api/datos')
def datos():
    # aquí van tus datos de prueba
    return jsonify({
        "status": "ok",
        "canales": [
            {"nombre": "Canal 1", "url": "https://..."},
            {"nombre": "Canal 2", "url": "https://..."}
        ]
    })

if __name__ == '__main__':
    app.run()
