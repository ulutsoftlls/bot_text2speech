from flask import Flask, request, jsonify
from text2speech import TTS
app = Flask(__name__)

@app.route('/api/receive_data', methods=['POST'])
def receive_data():
    received_data = request.json  # Assuming the data is sent as JSON
    #print(received_data)
    if received_data['gender'] == 'man':
    	
    	audio_url = obj.convert(received_data['text'])
    	response_data = {"audio_url": audio_url}
    elif received_data['gender'] == 'woman':
    	
    	audio_url = obj2.convert(received_data['text'])
    	response_data = {"audio_url": audio_url}
    
    return jsonify(response_data)

if __name__ == '__main__':
    
    obj = TTS('Нурбек', 48)
    obj2 = TTS('Нурай', 48)
    app.run(host='127.0.0.1', port=4050, debug=True)
