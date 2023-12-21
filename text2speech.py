
import soundfile as sf

import numpy as np
import torch
import time
import subprocess
from hparams import create_hparams
from model import Tacotron2
from layers import TacotronSTFT
from audio_processing import griffin_lim
from train import load_model
from text import text_to_sequence
from denoiser import Denoiser
import json
import os
from convert_number_to_text import ConvertNumberToString
from numberworks import numberreader

converter_number_to_text = ConvertNumberToString()
class TTS:
    def __init__(self, voice, symbols):
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        self.file_dir = voice
        self.hparams = create_hparams("distributed_run=False,mask_padding=False")
        self.hparams.n_symbols = symbols
        self.checkpoint_path = self.config.get('model').get(voice).get('model')
        self.model = load_model(self.hparams)
        self.model.load_state_dict(torch.load(self.checkpoint_path)['state_dict'])
        _ = self.model.cuda().eval().half()
        self.waveglow_path = self.config.get('model').get(voice).get('waveglow')
        self.waveglow = torch.load(self.waveglow_path)['model']
        self.waveglow.cuda().eval().half()
        for m in self.waveglow.modules():
            if 'Conv' in str(type(m)):
                setattr(m, 'padding_mode', 'zeros')
        for k in self.waveglow.convinv:
            k.float()
        # denoiser = Denoiser(self.waveglow)
    def convert(self, text):
        text.strip()
        
        if text.isdigit():
            t = int(text)
            if t<1500:
                text = "Бул,  " + text + " деген сан!"
        
        text = numberreader(text)
        cyrillic_letters = u"абвгдеёжзийклмнңоөпрстуүфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНҢОӨПРСТУҮФХЦЧШЩЪЫЬЭЮЯabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        stripped =  "".join([c for c in text if c in cyrillic_letters])
        
        if len(stripped)<5:
            return
        
        audio_list = []
        text = self.text_handler(text)
        final_sample = None
        #for i in text:
            #print("len = ",len(i), i)
        for i in text:
            sequence = np.array(text_to_sequence(i, ['basic_cleaners']))[None, :]
            sequence = torch.autograd.Variable(
                torch.from_numpy(sequence)).cuda().long()
            mel_outputs, mel_outputs_postnet, _, alignments = self.model.inference(sequence)
            with torch.no_grad():
                audio = self.waveglow.infer(mel_outputs_postnet, sigma=0.666)
                audio_np = audio[0].data.cpu().numpy().astype(np.float32)
            if final_sample is not None:
                final_sample = np.concatenate((final_sample, audio_np), axis=None)
            else:
                final_sample = audio_np
        filename = str(time.time())
        output_file = f"{self.file_dir}/{filename}"
        sf.write(output_file+".wav", final_sample, self.hparams.sampling_rate)

        self.convert_wav_to_mp3(output_file+'.wav', output_file+'.mp3')
        os.remove(output_file+".wav")
        return output_file
    def convert_wav_to_mp3(self,wav_file_path, mp3_file_path):
        subprocess.run(["lame", wav_file_path, mp3_file_path])
        
    def update_model(self, voice):
        #print('update model')
        self.checkpoint_path = self.config.get('model').get(voice).get('model')
        self.model = load_model(self.hparams)
        self.model.load_state_dict(torch.load(self.checkpoint_path)['state_dict'])
        _ = self.model.cuda().eval().half()
        self.file_dir = voice
        self.waveglow_path = self.config.get('model').get(voice).get('waveglow')
        self.waveglow = torch.load(self.waveglow_path)['model']
        self.waveglow.cuda().eval().half()
        for m in self.waveglow.modules():
            if 'Conv' in str(type(m)):
                setattr(m, 'padding_mode', 'zeros')
        for k in self.waveglow.convinv:
            k.float()
    def text_handler(self, text):
        text = self.lat_to_kir(text)
        #print(text)
        txt_list = []
        txtlen = len(text)
        if txtlen<151:
            txt_list.append(text)
            return txt_list
        text = text.replace(".", ". ")
        #text = text.replace(",", ",. ")
        text = text.replace("?", "?. ")
        text = text.replace("!", "!. ")
        text = text.replace(":", ":. ")
        text = text.replace(";", ";. ")
        txtlen = len(text)
        sentences = text.split(".")
        for s in sentences:
            if s[-1] in ",?!:;":
                pass
            else:
                s += "."
            ss = s.strip()
            if len(ss)<5:
                continue
            if len(ss)<151:
                txt_list.append(ss)
                #print("ss = ", ss)
            else:
                this_sentence = ""
                counter = 0
                words = ss.split()
                t150 = int(txtlen/150)+1
                tmax = int(txtlen/t150)
                for w in words:
                    w = w.strip()
                    z = len(w)
                    if z==0:
                        continue
                    if z>120:
                        continue
                    counter += z
                    
                    this_sentence += " "+w
                    if counter>tmax:
                        this_sentence = this_sentence[1:]
                        txt_list.append(this_sentence)
                        counter=0
                        this_sentence = ""
                            
                            
                if len(this_sentence)>0:
                    txt_list.append(this_sentence)
                        
        return txt_list
    def lat_to_kir( self, text):
        d = {"a":"а", "b":"б", "c":"с", "d":"д", "e":"е", "f":"ф", "g":"г", "h":"х", "i":"и", "j":"ж", "k":"к", "l":"л", "m":"м","n":"н", "o":"о", "p":"п", "q":"кю", "r":"р", "s":"с", "t":"т", "u":"у", "v":"в", "w":"в", "x":"кс","y":"у", "z":"з","A":"а", "B":"б", "C":"с", "D":"д", "E":"е", "F":"ф", "G":"г", "H":"х", "I":"и", "J":"ж", "K":"к", "L":"л", "M":"м","N":"н", "O":"о", "P":"п", "Q":"кю", "R":"р", "S":"с", "T":"т", "U":"у", "V":"в", "W":"в", "X":"кс","Y":"у", "Z":"з"}
        for key, value in d.items():
            text = text.replace(key, value)
        return text     	
