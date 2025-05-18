# Interprefy — Live Desktop Audio Interpreter

Struggling with language barriers or trying to understand a foreign movie? **Interprefy** is a live audio interpretation desktop app that captures your system’s audio, transcribes it in real-time, translates it into your selected language, and displays dynamic subtitles on screen.

> Built by **Ryan Qi** and **Tony Tan** at **JAMHacks**

---

# Languages/Tools

- Python 3.10+
- PyQt5
- VB-Audio Cable
- DeepGram API (real-time audio streaming)
- OpenAI fast-whisper (Speech-to-text)
- DeepL / Google Translate API (Translation)

---

# Technical Breakdown

- **Audio Pipeline**: Captures system audio using VB-Audio Cable and routes it to an internal microphone.
- **Speech Recognition**: Streams live audio using DeepGram to transcribe it using OpenAI's fast-whisper API.
- **Live Translation**: Sends transcript through DeepL/Google Translate API and receives the translation.
- **Overlay Display**: Shows translations as live subtitles in a PyQt5-based GUI.
- **History Logging**: Automatically logs all transcribed and translated conversations for review.
- **Multilingual**: Supports multiple translation languages selectable through settings.

---

# Requirements

### Python Version
```bash
Python 3.10 or higher
```

# Preview
**Home Page**
![image](https://github.com/user-attachments/assets/f4870966-3e4e-45fc-a4b1-a4899ee0b2e1)

**Settings Page**
![image](https://github.com/user-attachments/assets/28f76184-bbef-4cfe-b192-b242be95465a)

**History Logs**
![image](https://github.com/user-attachments/assets/0d511436-0956-470a-b384-0fedffaf335a)


