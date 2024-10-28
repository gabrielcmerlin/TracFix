import pandas as pd
import numpy as np
import math
import gdown
import matplotlib.pyplot as plt
import whisperx
import gc
import transformers
import webvtt
import os
import ffmpeg
import random
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from moviepy.editor import *
import torchaudio
from sklearn.neighbors import kneighbors_graph
import networkx as nx
import cv2
import glob
import re
from sentence_transformers import SentenceTransformer
from deepface import DeepFace
from src.models import Wav2Vec2ForSpeechClassification, HubertForSpeechClassification
from transformers import AutoConfig, Wav2Vec2FeatureExtractor
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from transformers import RobertaTokenizerFast, BertForSequenceClassification

!pip install git+https://github.com/m-bain/whisperX.git

class VideoEmotionRecognition:
    def __init__(self, mp4):

        logging.basicConfig(filename="newfile.log",
        format='%(asctime)s %(message)s',filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.logger.info("Initializing the class")

        self.dataframe = -1
        self.mp4 = mp4

        self.logger.info("Loading the arousal_valence map")

        url1 = 'https://drive.google.com/uc?id=1yJBHU8Zl4MuoQfJqkPgVDwJfYRJDPUAH'
        output = 'emotions_coord.xlsx'
        gdown.download(url1, output, quiet=False)
        self.emotions_coord = pd.read_excel(output)

        self.logger.info("Successfully initialized")

    def add_emotions(self, new_emotions):
        """
          Use this to add the arousal and valence of a new emotion by passing a series or a dataframe with it's name, x coordinate
        and y coordinate in this order . Useful when changing the model so that the emotions classified by this model are recognized
        """
        self.emotions_coords = pd.concat([self.emotions_coords,new_emotions])
        self.emotions_coords.reset_index(inplace=True, drop=True)

    def transcript(self, method = "whisperx", min_time = 1):
        """
          Transform the audio of a video into a dataframe with it's phrases in text form separated by time frames
        """
        self.logger.info("Running the whisperx transcription")
        bashCommand = "whisperx --compute_type float32 --output_format vtt " + self.mp4
        os.system(bashCommand)
        self.logger.info("Successfully transcripted")

        self.logger.info("Generating the Dataframe from the vtt")
        self.set_vtt(self.mp4.replace("mp4", "vtt"))

        self.dataframe = self.dataframe[self.dataframe.apply(lambda x: time_diff(x[1], x[0]), axis=1) > min_time]
        self.dataframe.reset_index(inplace = True, drop = True)

        self.logger.info("Successfully generated the dataframe")