import os
import speech_recognition as sr
from gtts import gTTS
from telethon import events
from pydub import AudioSegment

async def setup(client):
    # --- 1. TEXT TO VOICE (.voice) ---
    @client.on(events.NewMessage(pattern=r"\.voice$", outgoing=True))
    async def text_to_voice(event):
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("`❌ Kisi text message pe reply karo lode!`")
        
        await event.edit("`Converting Text to Voice... 🎤`")
        try:
            tts = gTTS(text=reply.text, lang='hi') # Hindi support ke liye
            file_path = "voice.mp3"
            tts.save(file_path)
            
            await event.client.send_file(
                event.chat_id, 
                file_path, 
                voice_note=True, 
                reply_to=reply.id
            )
            await event.delete()
            if os.path.exists(file_path): os.remove(file_path)
        except Exception as e:
            await event.edit(f"❌ **Error:** `{str(e)}`")

    # --- 2. VOICE TO TEXT (.text) ---
    @client.on(events.NewMessage(pattern=r"\.text$", outgoing=True))
    async def voice_to_text(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await event.edit("`❌ Kisi voice message pe reply kar bsdk!`")
        
        await event.edit("`Listening to Voice... 📝`")
        
        try:
            # Voice file download karo
            path = await reply.download_media(file="voice_temp.ogg")
            
            # OGG ko WAV mein badlo (SpeechRecognition ke liye zaruri hai)
            dest = "voice_temp.wav"
            audio = AudioSegment.from_file(path)
            audio.export(dest, format="wav")
            
            # Recognize karo
            r = sr.Recognizer()
            with sr.AudioFile(dest) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language='hi-IN') # Hindi/English mix recognize karega
            
            await event.edit(f"📝 **Voice to Text:**\n\n`{text}`")
            
            # Kachra saaf karo
            if os.path.exists(path): os.remove(path)
            if os.path.exists(dest): os.remove(dest)
            
        except Exception as e:
            await event.edit(f"❌ **Error:** `{str(e)}` (Ya toh voice clear nahi hai ya FFmpeg install nahi hai)")

