# 🎯 AI Goal Compass

An intelligent project analysis and management system built with Streamlit, CrewAI, and Ollama.

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - ⚡ 60-second quick start guide (START HERE!)
- **[README.md](README.md)** - Main documentation (you are here)
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - 🎉 Complete implementation summary
- **[VOICE_INPUT_GUIDE.md](VOICE_INPUT_GUIDE.md)** - Complete guide for voice-to-text features
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - Practical examples and use cases
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing checklist and procedures
- **[CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)** - Summary of all changes made
- **[APP_FLOW_DIAGRAM.md](APP_FLOW_DIAGRAM.md)** - Visual flow diagrams and architecture
- **[UI_SCREENSHOTS_DESCRIPTION.md](UI_SCREENSHOTS_DESCRIPTION.md)** - UI mockups and descriptions

## ✨ Features

- **📊 Project Overview Dashboard**: Get insights into all your projects at a glance
- **🔍 AI-Powered Analysis**: Use CrewAI agents with Ollama 3.2 to analyze project status and suggest optimal next steps
- **📊 Visual Flow Diagrams**: Mermaid-based visualization of project progress and workflow
- **➕ Project Creation**: Easy creation of new projects with structured markdown files
- **📁 Project Management**: Automatic scanning and organization of project folders
- **🎤 Voice-to-Text Input**: Record voice input and automatically transcribe it to text for project fields

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running locally
3. **Llama 3.2 model** pulled in Ollama

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AIGoalCompass
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Ollama**:
   ```bash
   # Install Ollama (if not already installed)
   # Visit: https://ollama.ai
   
   # Pull the Llama 3.2 model
   ollama pull llama3.2
   
   # Start Ollama service
   ollama serve
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

Each project in the `projects/` folder should have the following structure:

```
projects/
├── project_category/
│   └── project_name/
│       ├── goal.md      # Project objectives and requirements
│       ├── completed.md # Tasks that have been completed
│       └── next.md      # Next steps to achieve the goal
```

### Example Project Structure:
```
projects/
├── B2L/
│   └── platform/
│       ├── goal.md
│       ├── completed.md
│       └── next.md
├── personal/
│   └── website/
│       ├── goal.md
│       ├── completed.md
│       └── next.md
```

## 🎮 How to Use

### 1. 📊 Overview Dashboard
- View all projects with summary metrics
- See recent activity and project status
- Quick access to project details

### 2. 🔍 Project Analysis
- Select any project for AI-powered analysis
- Get strategic recommendations from CrewAI agents
- View detailed project information and timelines
- Edit projects with voice input support

### 3. 📊 Visual Flow Diagrams
- Automatic generation of Mermaid flow charts
- Visual representation of project progress
- Clear view of completed tasks and next steps

### 4. ➕ Create New Projects
- Easy project creation with guided forms
- Automatic folder structure generation
- Template-based project setup
- 🎤 Voice input support for all text fields

### 5. 🎤 Voice-to-Text Input
- Click the microphone button to record voice input
- Automatically transcribes speech to text
- Available for project creation and editing
- Supports multiple languages via Google Speech Recognition
- **See [VOICE_INPUT_GUIDE.md](VOICE_INPUT_GUIDE.md) for detailed instructions**

## 🤖 AI Analysis Features

The application uses **CrewAI** with two specialized agents:

1. **Project Analyst Agent**: 
   - Analyzes project goals and current status
   - Identifies gaps between objectives and completed work
   - Suggests optimal next steps

2. **Strategic Advisor Agent**:
   - Provides strategic insights and prioritization
   - Recommends resource allocation
   - Identifies risks and dependencies

## ⚙️ Configuration

### Ollama Settings
- **Model**: llama3.2 (configurable)
- **Host**: localhost:11434 (default)
- **Timeout**: 60 seconds

### Project Directory
- **Default**: `./projects/`
- **Configurable**: Can be changed in the Settings page

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **AI Framework**: CrewAI
- **LLM**: Ollama (Llama 3.2)
- **Visualization**: Mermaid, Plotly
- **Data Processing**: Pandas
- **File Management**: Pathlib
- **Voice Recognition**: SpeechRecognition, streamlit-mic-recorder

## 📝 Usage Tips

1. **Keep goals specific**: Write clear, measurable objectives in `goal.md`
2. **Update completed tasks**: Regularly update `completed.md` with finished work
3. **Define next steps**: Use `next.md` for immediate actionable items
4. **Use AI analysis**: Leverage the AI agents for strategic guidance
5. **Visual planning**: Use flow diagrams to understand project structure
6. **Voice input**: Use the microphone button to quickly add content via voice
7. **Clear speech**: Speak clearly and at a moderate pace for best transcription results

## 🔧 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve
```

### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Project Not Showing
- Ensure `goal.md` exists in the project folder
- Check file permissions
- Use the "Refresh Projects" button in Settings

### Voice Input Not Working
- Verify microphone permissions in your browser
- Install required packages: `pip install streamlit-mic-recorder SpeechRecognition`
- Check internet connection (required for Google Speech Recognition)
- See [VOICE_INPUT_GUIDE.md](VOICE_INPUT_GUIDE.md) for detailed troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Export/import project templates
- [ ] Integration with external project management tools
- [ ] Advanced analytics and reporting
- [ ] Team collaboration features
- [ ] Mobile responsive design improvements

---

**Happy Project Managing! 🚀** 
