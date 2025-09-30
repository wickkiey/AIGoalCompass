# App Flow with Voice Input

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Goal Compass                           │
│          🎯 Intelligent Project Management                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │          🧭 Navigation Menu              │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────┐                           ┌──────────────────┐
│ 📊 Overview  │                           │ 🔍 Analysis      │
└──────────────┘                           └──────────────────┘
    │                                           │
    ├─ View Metrics                             ├─ 📖 Project Details
    ├─ Project List                             ├─ 🤖 AI Analysis
    └─ Quick Stats                              ├─ 📊 Visual Flow
                                                └─ ✏️ Edit Project
                                                        │
                                                        └─ 🎤 Voice Input
        │                                           │
        ▼                                           ▼
┌───────────────┐                         ┌──────────────────┐
│ ➕ Create      │                         │ ⚙️ Settings      │
│    Project     │                         └──────────────────┘
└───────────────┘                                  │
        │                                          ├─ Ollama Config
        ├─ Project Form                            ├─ Directory Path
        │   ├─ Parent Dir                          └─ Refresh Option
        │   ├─ Project Name
        │   ├─ Goal 🎤
        │   ├─ Completed 🎤
        │   └─ Next Steps 🎤
        │
        └─ 🎤 Voice Input Helper
            ├─ Goal Recording
            ├─ Completed Recording
            └─ Next Steps Recording
```

## Voice Input Workflow

### Creating a Project with Voice

```
User Action              │  System Response
─────────────────────────┼────────────────────────────────
1. Click Create Project  │  Shows project form
                         │  Shows voice input helper
                         │
2. Click 🎤 Record       │  Requests mic permission
                         │  Starts recording
                         │
3. User speaks           │  Audio buffer collecting
                         │
4. Click ⏹️ Stop         │  Sends audio to Google API
                         │  Displays "Processing..."
                         │
5. Transcription done    │  Shows transcribed text
                         │  ✅ Success message
                         │
6. Copy text             │  Text ready to paste
                         │
7. Paste into form       │  Form updated with content
                         │
8. Submit form           │  Creates project files
                         │  Shows success + balloons 🎈
```

### Editing a Project with Voice

```
User Action              │  System Response
─────────────────────────┼────────────────────────────────
1. Select project        │  Shows project details
                         │
2. Go to Edit tab        │  Shows edit form
                         │  Shows current content
                         │  Shows voice input helper
                         │
3. Click 🎤 Record       │  Starts voice recording
                         │
4. Speak updates         │  Audio being captured
                         │
5. Stop recording        │  Transcribes audio
                         │  Shows transcribed text
                         │
6. Copy to form field    │  Appends/updates field
                         │
7. Save changes          │  Updates project files
                         │  Shows success message
```

## Voice Recognition Flow

```
┌─────────────────┐
│  User speaks    │
│   into mic      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Browser captures       │
│  audio via WebRTC       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  streamlit-mic-recorder │
│  converts to bytes      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Save to temp WAV file  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  SpeechRecognition lib  │
│  reads audio file       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Google Speech API      │
│  (requires internet)    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Returns text           │
│  transcription          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Display to user        │
│  in text area           │
└─────────────────────────┘
```

## Error Handling Flow

```
┌──────────────────┐
│  Voice Input     │
│  Initiated       │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────┐
│  Check mic permission   │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  ✅ Yes     ❌ No
    │         │
    │         └──► Show permission error
    │              Ask user to allow mic
    │
    ▼
┌─────────────────────────┐
│  Start recording        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Audio quality check    │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  ✅ Good   ❌ Poor
    │         │
    │         └──► Warning: Check mic/noise
    │              Suggest retry
    │
    ▼
┌─────────────────────────┐
│  Send to API            │
└────────┬────────────────┘
         │
    ┌────┴────────┐
    │             │
    ▼             ▼
  ✅ Success   ❌ Error
    │             │
    │             ├──► Network error
    │             │    (No internet)
    │             │
    │             ├──► API error
    │             │    (Service down)
    │             │
    │             └──► Unknown audio
    │                  (Unclear speech)
    │
    ▼
┌─────────────────────────┐
│  Show transcribed text  │
└─────────────────────────┘
```

## Feature Detection

```
┌──────────────────────────┐
│  App Initialization      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Try import              │
│  streamlit_mic_recorder  │
└──────────┬───────────────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
    ✅ OK     ❌ Fail
      │         │
      │         └──► MIC_RECORDER_AVAILABLE = False
      │              Show install message
      │              Voice buttons disabled
      │
      └──► MIC_RECORDER_AVAILABLE = True
           Show voice buttons
           Enable voice features
```

## UI Component Structure

```
Create Project Page
├── Header
│   └── Info banner (voice status)
├── Form (inside st.form)
│   ├── Parent Directory input
│   ├── Project Name input
│   ├── Goal text area
│   ├── Completed text area
│   ├── Next Steps text area
│   └── Submit button
└── Voice Input Helper (outside form)
    ├── Goal Voice Section
    │   ├── 🎤 Record button
    │   └── Transcribed text area
    ├── Completed Voice Section
    │   ├── 🎤 Record button
    │   └── Transcribed text area
    └── Next Steps Voice Section
        ├── 🎤 Record button
        └── Transcribed text area

Edit Project Tab
├── Info banner (voice status)
├── Edit Form (inside st.form)
│   ├── Goal text area (pre-filled)
│   ├── Completed text area (pre-filled)
│   ├── Next Steps text area (pre-filled)
│   └── Save button
└── Voice Input Helper (outside form)
    ├── Goal Voice Section
    ├── Completed Voice Section
    └── Next Steps Voice Section
```

## State Management

```
Session State Keys Used:
├── goal_text
├── completed_text
├── next_steps_text
├── edit_goal
├── edit_completed
├── edit_next
├── goal_voice
├── completed_voice
├── next_voice
├── edit_goal_voice
├── edit_completed_voice
└── edit_next_voice

Form State:
├── new_project_form (Create page)
└── edit_project_form (Edit tab)

Component State:
└── mic_recorder instances (multiple)
    ├── Track recording status
    ├── Store audio bytes
    └── Trigger transcription
```

## Data Flow

```
┌──────────────────┐
│  User Input      │
│  (Voice/Text)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  Form Fields         │
│  (Streamlit state)   │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Submit Handler      │
│  (on form submit)    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  ProjectManager      │
│  create_project()    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  File System         │
│  ├── goal.md         │
│  ├── completed.md    │
│  └── next.md         │
└──────────────────────┘
```

---

This diagram shows the complete application flow with voice input integration.
