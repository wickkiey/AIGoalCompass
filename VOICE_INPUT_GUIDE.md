# 🎤 Voice Input Guide

## Overview

AI Goal Compass now includes voice-to-text functionality, allowing you to create and edit projects using your voice. This feature makes it easier and faster to capture your thoughts and ideas.

## Features

- **Real-time transcription**: Convert speech to text instantly
- **Multiple input fields**: Voice input available for all text areas
- **Easy to use**: Click the microphone button to start recording
- **Multi-language support**: Supports multiple languages via Google Speech Recognition

## How to Use Voice Input

### 1. Creating a New Project with Voice

1. Navigate to the **➕ Create Project** page
2. You'll see microphone icons (🎤) throughout the interface
3. Click the **🎤 Record** button next to any field
4. Speak clearly into your microphone
5. Click **⏹️ Stop** when finished
6. The transcribed text will appear in the designated area
7. Copy and paste the transcribed text into the form fields

### 2. Editing a Project with Voice

1. Go to **🔍 Analysis** page
2. Select a project to analyze
3. Click on the **✏️ Edit Project** tab
4. Use the voice input helper section at the bottom
5. Record your updates for any field
6. Copy the transcribed text to the appropriate field in the form
7. Click **💾 Save Changes**

### 3. Voice Input Helper

The Voice Input Helper section provides dedicated recording areas for:
- 🎯 **Project Goal**: Record your project objectives
- ✅ **Completed Tasks**: Record what you've accomplished
- 📝 **Next Steps**: Record your action items

## Tips for Best Results

1. **Speak clearly**: Enunciate your words for better accuracy
2. **Moderate pace**: Don't speak too fast or too slow
3. **Quiet environment**: Minimize background noise
4. **Good microphone**: Use a quality microphone for better results
5. **Short segments**: Record in shorter segments for easier editing
6. **Review and edit**: Always review the transcribed text before submitting

## Supported Languages

The voice recognition uses Google's Speech Recognition API, which supports:
- English (US, UK, Australia, Canada, India)
- Spanish
- French
- German
- Italian
- Portuguese
- Russian
- Chinese (Mandarin, Cantonese)
- Japanese
- Korean
- And many more...

## Troubleshooting

### Voice input not available
**Problem**: You see "Voice input unavailable" message  
**Solution**: Install the required package:
```bash
pip install streamlit-mic-recorder
```

### Microphone not working
**Problem**: Recording button doesn't capture audio  
**Solution**: 
- Check browser permissions for microphone access
- Ensure your microphone is properly connected
- Try a different browser (Chrome or Edge recommended)

### Poor transcription quality
**Problem**: Transcribed text doesn't match what you said  
**Solution**:
- Speak more clearly and slowly
- Move closer to the microphone
- Reduce background noise
- Try recording shorter segments

### Network errors
**Problem**: "Could not request results from speech recognition service"  
**Solution**:
- Check your internet connection (Google Speech Recognition requires internet)
- Verify you can access Google services
- Try again after a few moments

## Privacy and Security

- Voice data is processed through Google's Speech Recognition API
- Audio is not stored on our servers
- Transcription happens in real-time and is immediately discarded
- All data remains local to your project files

## Browser Compatibility

Voice input works best with:
- ✅ Google Chrome (Recommended)
- ✅ Microsoft Edge
- ✅ Firefox (may require additional permissions)
- ⚠️ Safari (limited support)

## Feature Requirements

- Active internet connection (for Google Speech Recognition)
- Browser microphone permissions
- Python package: `streamlit-mic-recorder`
- Python package: `SpeechRecognition`

## Keyboard Shortcuts

While recording:
- **Click Stop button**: Finish recording
- **Click Start again**: Record additional content

## Examples

### Creating a Project Goal via Voice
1. Click 🎤 in the Goal Voice Input section
2. Say: "Create a mobile app for task management with user authentication, task creation, and notification features"
3. Click ⏹️ Stop
4. Review the transcribed text
5. Copy to the Goal field

### Adding Completed Tasks via Voice
1. Click 🎤 in the Completed Tasks Voice Input section
2. Say: "Set up development environment. Created initial project structure. Implemented user authentication. Built task creation interface."
3. Click ⏹️ Stop
4. Review and copy to the Completed Tasks field

### Recording Next Steps via Voice
1. Click 🎤 in the Next Steps Voice Input section
2. Say: "Implement notification system. Add task editing functionality. Create user dashboard. Deploy to production."
3. Click ⏹️ Stop
4. Review and copy to the Next Steps field

## Support

If you encounter any issues with voice input:
1. Check this guide for troubleshooting steps
2. Verify your microphone and browser permissions
3. Ensure you have an active internet connection
4. Check the console for error messages

---

**Happy voice recording! 🎤**
