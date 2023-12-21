import matplotlib
import matplotlib.pylab as plt
import IPython.display as ipd

import soundfile as sf

import numpy as np
import torch


from hparams import create_hparams
from model import Tacotron2
from layers import TacotronSTFT
from audio_processing import griffin_lim
from train import load_model
from text import text_to_sequence
from denoiser import Denoiser



hparams = create_hparams("distributed_run=False,mask_padding=False")

checkpoint_path = "models/checkpoint_6000"
model = load_model(hparams)
model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
_ = model.cuda().eval().half()


waveglow_path = 'models/waveglow_v5.pt'
waveglow = torch.load(waveglow_path)['model']
waveglow.cuda().eval().half()
for k in waveglow.convinv:
    k.float()
denoiser = Denoiser(waveglow)



text = "Ошондой эле палестин министри алака.."
#text = "1 2 3"
sequence = np.array(text_to_sequence(text, ['basic_cleaners']))[None, :]
sequence = torch.autograd.Variable(
    torch.from_numpy(sequence)).cuda().long()



mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)

output_folder = "check"  

with torch.no_grad():
    audio = waveglow.infer(mel_outputs_postnet, sigma=0.666)
    audio_np = audio[0].data.cpu().numpy().astype(np.float32)
print(audio)
output_file = f"check/m_generated_audio.wav"
sf.write(output_file, audio_np, hparams.sampling_rate)
