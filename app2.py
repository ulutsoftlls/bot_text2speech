from flask import Flask, request, send_file
from text2speech import TTS
from io import BytesIO
app = Flask(__name__)

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    received_data = request.json  # Assuming the data is sent as JSON
    #print(received_data)
    if received_data['gender'] == 'man':
    	
    	audio_url = obj.convert(received_data['text'])
    	#response_data = {"audio_url": audio_url}
    elif received_data['gender'] == 'woman':
    	
    	audio_url = obj2.convert(received_data['text'])
    	#response_data = {"audio_url": audio_url}
    
    
    generated_audio = BytesIO(audio_url)

    # Возвращаем StreamingResponse с байтовым потоком и указываем media_type
    return send_file(generated_audio, as_attachment=True)

if __name__ == '__main__':
    
    obj = TTS('Нурбек', 48)
    obj2 = TTS('Нурай', 48)
    app.run(host='80.72.180.130', port=6060, debug=True)
