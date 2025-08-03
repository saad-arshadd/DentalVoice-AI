import assemblyai as aai
from elevenlabs import generate, stream , voices
import threading
from openai import OpenAI

class VOICEBOT:
    def __init__(self):
        aai.settings.api_key = "9771bdd563404efb8e4ac80a85ce4be1"
        self.openai_client = OpenAI(api_key="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")
        self.elevenlabs_api_key ="sk_4eaf51fd43227d8088ab560774f92dd0f36b8c28d97f7f36"

        self.transcriber= None
        # prompt for the intitialization
        self.full_trans=[
            {"role":"system", "content":"you are a receptionist at a dental clinic , be resourceful and efficient"}


        ]
     # creating a method for real time speec to text transcription with the help of assembly ai

    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16000,
            on_data =self.on_data,
            on_error = self.on_error,
            on_open= self.on_open,
            on_close= self.on_close,
            end_utterance_silence_threshold =1000  #will wait in 1000ms until this tie to check if wwe have actually ended a sentence

        )
         #the below code connects to your microphone and streams your voice text to assembly ai
        self.transcriber.connect()
        mic_stream=aai.extras.MicrophoneStream(sample_rate=16000)
        self.transcriber.stream(mic_stream)

    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return

    def on_data(self, transcript: aai.RealtimeTranscript): #whenever assembly ai transcriber will send back trancsiption data
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript): ##here we recieve the final real time trnscript when we finish a sentence
            self.generate_ai_response(transcript) #send the final text transcribed sentence to this function to now generate the api response of you spoken sentence
        else: # if your senetcne is not final , stil speaking <1000ms , then pritn the partial result
            print(transcript.text, end="\r")

    def on_error(self, error: aai.RealtimeError):
        #print("An error occured:", error)
        return

    def on_close(self):
        # print("Closing Session")
        return

    #next step , passing transcibed data from assembly ai (function on data ) to open ai to generate response

    def generate_ai_response(self, transcript):
        # first we need to stop transcription from assembly ai while we are generating response form our open ai
        self.stop_transcription()
#now add real time traanscript to full transcript list for the user

        self.full_trans.append({"role":"user", "content":transcript.text})
#now we want to print real time transcript which the user has just said

        print(f"\nUser:{transcript.text}",end="\r\n")
#now we will be passing this trnscript directly to open ai's api

        response=self.openai_client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages = self.full_trans

        )
# now we will save the response generated from gpt in ai response variable
        ai_response=response.choices[0].message.content


#now we will generate audio
        self.generate_audio(ai_response)


#once we are done with the audio , now we can restart the real time trancription speech to te text again from the user

        self.start_transcription()


#now we are at our last step to generate audio from text to speech using eleven labs

    def generate_audio(self ,text): # the text here is the response from the open ai api

        self.full_trans.append({"role":"assistant", "content":text})

# now printing the ai generated response
        print(f"\nAssistant :{text}")



        # List and print all voices available for your API key
        #for voice in voices():
         #   print(f"Name: {voice.name}, Voice ID: {voice.voice_id}")

        #now requesting eleven lab apis to generate the audio using a pre defned function called generate

        audio_stream = generate(
            api_key=self.elevenlabs_api_key,
            text=text,
            voice = "Sarah",
            stream=True
        )

        stream(audio_stream)


start_greeting = "Thank You for callings us , how may I assist you "

ai_ASS = VOICEBOT()
ai_ASS.generate_audio(start_greeting)
ai_ASS.start_transcription()























