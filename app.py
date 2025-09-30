import streamlit as st
import os
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from typing import Dict, List, Any
import markdown
import speech_recognition as sr

# CrewAI and Ollama imports
from crewai import Agent, Task, Crew, Process
from langchain_ollama import OllamaLLM

# Import mic recorder
try:
    from streamlit_mic_recorder import mic_recorder
    MIC_RECORDER_AVAILABLE = True
except ImportError:
    MIC_RECORDER_AVAILABLE = False

# Set page config
st.set_page_config(
    page_title="AI Goal Compass - Project Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def transcribe_audio(audio_bytes):
    """Convert audio bytes to text using speech recognition"""
    if audio_bytes is None:
        return ""
    
    recognizer = sr.Recognizer()
    
    try:
        # Save audio bytes to a temporary file
        import io
        import wave
        import tempfile
        
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        # Read the audio file
        with sr.AudioFile(tmp_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return text
    except sr.UnknownValueError:
        st.warning("Could not understand the audio. Please try again.")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results from speech recognition service: {e}")
        return ""
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return ""

def voice_input_field(label: str, help_text: str, height: int = 150, key_prefix: str = ""):
    """Create a text area with voice input capability"""
    st.markdown(f"**{label}**")
    
    col_text, col_voice = st.columns([4, 1])
    
    with col_text:
        text_value = st.text_area(
            label,
            height=height,
            help=help_text,
            key=f"{key_prefix}_text",
            label_visibility="collapsed"
        )
    
    with col_voice:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if MIC_RECORDER_AVAILABLE:
            audio = mic_recorder(
                start_prompt="🎤 Record",
                stop_prompt="⏹️ Stop",
                just_once=False,
                use_container_width=True,
                key=f"{key_prefix}_mic"
            )
            
            if audio:
                st.success("✅ Recorded")
                transcribed_text = transcribe_audio(audio['bytes'])
                if transcribed_text:
                    # Append transcribed text to existing text
                    if text_value:
                        st.session_state[f"{key_prefix}_text"] = text_value + "\n" + transcribed_text
                    else:
                        st.session_state[f"{key_prefix}_text"] = transcribed_text
                    st.rerun()
        else:
            st.info("🎤\n\nVoice input unavailable")
    
    return text_value

class ProjectManager:
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
    
    def scan_projects(self) -> Dict[str, Dict[str, Any]]:
        """Scan all projects and return their details"""
        projects = {}
        
        for project_path in self.projects_dir.rglob("goal.md"):
            # Get project identifier from path
            relative_path = project_path.relative_to(self.projects_dir)
            project_id = str(relative_path.parent).replace(os.sep, "_")
            
            project_data = {
                "path": project_path.parent,
                "goal": self._read_file_safe(project_path),
                "completed": self._read_file_safe(project_path.parent / "completed.md"),
                "next": self._read_file_safe(project_path.parent / "next.md"),
                "last_modified": datetime.fromtimestamp(project_path.stat().st_mtime)
            }
            
            projects[project_id] = project_data
        
        return projects
    
    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            st.error(f"Error reading {file_path}: {e}")
            return ""
    
    def create_project(self, name: str, parent_dir: str, goal: str, completed: str = "", next_steps: str = "") -> bool:
        """Create a new project with the required markdown files"""
        try:
            project_path = self.projects_dir / parent_dir / name
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create the markdown files
            (project_path / "goal.md").write_text(goal, encoding='utf-8')
            (project_path / "completed.md").write_text(completed, encoding='utf-8')
            (project_path / "next.md").write_text(next_steps, encoding='utf-8')
            
            return True
        except Exception as e:
            st.error(f"Error creating project: {e}")
            return False
    
    def update_project(self, project_path: Path, goal: str, completed: str, next_steps: str) -> bool:
        """Update an existing project"""
        try:
            (project_path / "goal.md").write_text(goal, encoding='utf-8')
            (project_path / "completed.md").write_text(completed, encoding='utf-8')
            (project_path / "next.md").write_text(next_steps, encoding='utf-8')
            return True
        except Exception as e:
            st.error(f"Error updating project: {e}")
            return False

class ProjectAnalyzer:
    def __init__(self):
        self.llm = OllamaLLM(model="llama3.2")
        
        # Define CrewAI agents
        self.analyst_agent = Agent(
            role='Project Analyst',
            goal='Analyze project goals, completed tasks, and suggest optimal next steps',
            backstory='You are an experienced project manager and business analyst with expertise in breaking down complex projects into actionable steps.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.strategist_agent = Agent(
            role='Strategic Advisor',
            goal='Provide strategic insights and prioritization for project tasks',
            backstory='You are a strategic advisor who excels at identifying critical paths and optimizing project workflows.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def analyze_project(self, goal: str, completed: str, next_steps: str) -> Dict[str, str]:
        """Analyze a project using CrewAI agents"""
        
        # Define tasks
        analysis_task = Task(
            description=f"""
            Analyze this project:
            
            GOAL: {goal}
            
            COMPLETED: {completed}
            
            CURRENT NEXT STEPS: {next_steps}
            
            Analyse the project and provide a detailed analysis of the project, including a gap analysis, optimal next steps, and risk assessment.
            """,
            expected_output=f"""Clean Markdown formatted below output
            Provide:
            1. Current project status assessment
            2. Gap analysis between goal and completed work
            3. Optimal sequence of next steps
            4. Risk assessment and mitigation strategies.""",
            agent=self.analyst_agent
        )
        
        strategy_task = Task(
            description=f"""
            Based on the project analysis, provide strategic recommendations:

            1. Prioritized action items with timelines
            2. Resource requirements
            3. Success metrics and milestones
            4. Critical dependencies and blockers

            Focus on actionable, specific recommendations.
            """,
            expected_output=f"""Clean Markdown formatted below output
            Provide:
            1. A prioritized list of action items, each with suggested timelines
            2. A summary of resource requirements (people, tools, etc.)
            3. Defined success metrics and key milestones
            4. Identification of critical dependencies and potential blockers, with mitigation suggestions.
            """,
            agent=self.strategist_agent
        )
        
        # Create and run crew
        crew = Crew(
            agents=[self.analyst_agent, self.strategist_agent],
            tasks=[analysis_task, strategy_task],
            verbose=2,
            process=Process.sequential
        )
        
        try:
            result = crew.kickoff()
            return {
                "analysis": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "analysis": f"Error during analysis: {str(e)}",
                "status": "error"
            }
    
    def generate_flow_diagram(self, goal: str, completed: str, next_steps: str) -> str:
        """Generate a Mermaid flow diagram representing project progress"""
        
        # Simple parsing to create flow diagram
        completed_items = [item.strip("- ").strip() for item in completed.split('\n') if item.strip()]
        next_items = [item.strip("- ").strip() for item in next_steps.split('\n') if item.strip()]
        
        mermaid_diagram = "graph TD\n"
        mermaid_diagram += "    A[Project Goal] --> B[Completed Tasks]\n"
        
        # Add completed tasks
        for i, item in enumerate(completed_items[:5]):  # Limit to 5 items for readability
            if item:
                mermaid_diagram += f"    B --> C{i}[✅ {item[:30]}...]\n"
        
        mermaid_diagram += "    B --> D[Next Steps]\n"
        
        # Add next steps
        for i, item in enumerate(next_items[:5]):  # Limit to 5 items for readability
            if item:
                mermaid_diagram += f"    D --> E{i}[⏳ {item[:30]}...]\n"
        
        mermaid_diagram += "    D --> F[🎯 Goal Achievement]\n"
        
        return mermaid_diagram

def render_project_overview(projects: Dict[str, Dict[str, Any]]):
    """Render project overview dashboard"""
    st.header("📊 Project Overview Dashboard")
    
    if not projects:
        st.warning("No projects found. Create your first project using the sidebar!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Projects", len(projects))
    
    with col2:
        completed_projects = sum(1 for p in projects.values() if p['completed'].strip())
        st.metric("Active Projects", completed_projects)
    
    with col3:
        recent_projects = sum(1 for p in projects.values() 
                            if (datetime.now() - p['last_modified']).days <= 7)
        st.metric("Recently Updated", recent_projects)
    
    with col4:
        pending_projects = sum(1 for p in projects.values() if p['next'].strip())
        st.metric("With Next Steps", pending_projects)
    
    # Project list
    st.subheader("📋 Project List")
    
    project_data = []
    for project_id, data in projects.items():
        project_data.append({
            "Project": project_id.replace("_", " / "),
            "Goal Length": len(data['goal']),
            "Completed Tasks": "✅" if data['completed'].strip() else "❌",
            "Next Steps": "📝" if data['next'].strip() else "❌",
            "Last Modified": data['last_modified'].strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(project_data)
    st.dataframe(df, use_container_width=True)

def render_project_analyzer(projects: Dict[str, Dict[str, Any]], analyzer: ProjectAnalyzer):
    """Render project analysis interface"""
    st.header("🔍 AI Project Analysis")
    
    if not projects:
        st.warning("No projects available for analysis.")
        return
    
    # Project selection
    project_options = list(projects.keys())
    selected_project = st.selectbox(
        "Select Project to Analyze",
        project_options,
        format_func=lambda x: x.replace("_", " / ")
    )
    
    if selected_project:
        project_data = projects[selected_project]
        
        # Display project details
        st.subheader(f"📁 {selected_project.replace('_', ' / ')}")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📖 Project Details", "🤖 AI Analysis", "📊 Visual Flow", "✏️ Edit Project"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🎯 Goal:**")
                st.markdown(project_data['goal'][:500] + "..." if len(project_data['goal']) > 500 else project_data['goal'])
                
                st.markdown("**✅ Completed:**")
                completed_text = project_data['completed'] if project_data['completed'].strip() else "No completed tasks recorded"
                st.markdown(completed_text)
            
            with col2:
                st.markdown("**📝 Next Steps:**")
                next_text = project_data['next'] if project_data['next'].strip() else "No next steps defined"
                st.markdown(next_text)
                
                st.markdown("**📅 Last Modified:**")
                st.text(project_data['last_modified'].strftime("%Y-%m-%d %H:%M:%S"))
        
        with tab2:
            st.subheader("🤖 AI-Powered Analysis")
            
            if st.button("🚀 Analyze Project", type="primary"):
                with st.spinner("AI agents are analyzing your project..."):
                    analysis_result = analyzer.analyze_project(
                        project_data['goal'],
                        project_data['completed'],
                        project_data['next']
                    )
                
                if analysis_result['status'] == 'success':
                    st.success("Analysis completed!")
                    st.markdown("### 📋 Analysis Results")
                    st.markdown(analysis_result['analysis'])
                else:
                    st.error("Analysis failed. Please check your Ollama setup.")
                    st.error(analysis_result['analysis'])
        
        with tab3:
            st.subheader("📊 Project Flow Visualization")
            
            try:
                from streamlit_mermaid import st_mermaid
                
                flow_diagram = analyzer.generate_flow_diagram(
                    project_data['goal'],
                    project_data['completed'],
                    project_data['next']
                )
                
                st.markdown("**Project Progress Flow:**")
                st_mermaid(flow_diagram)
                
            except ImportError:
                st.warning("Mermaid visualization not available. Install streamlit-mermaid for flow diagrams.")
                
                # Fallback: Simple text-based flow
                st.markdown("**Project Flow (Text-based):**")
                st.markdown(f"🎯 **Goal** → ✅ **Completed Tasks** → ⏳ **Next Steps** → 🏆 **Success**")
        
        with tab4:
            st.subheader("✏️ Edit Project")
            
            if MIC_RECORDER_AVAILABLE:
                st.info("🎤 Voice input is enabled! Use the voice input helper below to update your project with voice.")
            
            with st.form("edit_project_form"):
                edit_goal = st.text_area(
                    "🎯 Project Goal",
                    value=project_data['goal'],
                    height=150,
                    key="edit_goal"
                )
                
                col_edit1, col_edit2 = st.columns(2)
                
                with col_edit1:
                    edit_completed = st.text_area(
                        "✅ Completed Tasks",
                        value=project_data['completed'],
                        height=150,
                        key="edit_completed"
                    )
                
                with col_edit2:
                    edit_next = st.text_area(
                        "📝 Next Steps",
                        value=project_data['next'],
                        height=150,
                        key="edit_next"
                    )
                
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    project_manager = ProjectManager()
                    if project_manager.update_project(
                        project_data['path'],
                        edit_goal,
                        edit_completed,
                        edit_next
                    ):
                        st.success("✅ Project updated successfully!")
                        st.rerun()
            
            # Voice input helper for editing
            if MIC_RECORDER_AVAILABLE:
                st.markdown("---")
                st.markdown("### 🎤 Voice Input Helper for Editing")
                
                voice_edit_col1, voice_edit_col2, voice_edit_col3 = st.columns(3)
                
                with voice_edit_col1:
                    st.markdown("**🎯 Add to Goal**")
                    edit_goal_audio = mic_recorder(
                        start_prompt="🎤 Record",
                        stop_prompt="⏹️ Stop",
                        just_once=False,
                        use_container_width=True,
                        key="edit_goal_voice"
                    )
                    
                    if edit_goal_audio:
                        transcribed = transcribe_audio(edit_goal_audio['bytes'])
                        if transcribed:
                            st.text_area("Transcribed:", value=transcribed, height=80, key="edit_goal_transcribed")
                
                with voice_edit_col2:
                    st.markdown("**✅ Add to Completed**")
                    edit_completed_audio = mic_recorder(
                        start_prompt="🎤 Record",
                        stop_prompt="⏹️ Stop",
                        just_once=False,
                        use_container_width=True,
                        key="edit_completed_voice"
                    )
                    
                    if edit_completed_audio:
                        transcribed = transcribe_audio(edit_completed_audio['bytes'])
                        if transcribed:
                            st.text_area("Transcribed:", value=transcribed, height=80, key="edit_completed_transcribed")
                
                with voice_edit_col3:
                    st.markdown("**📝 Add to Next Steps**")
                    edit_next_audio = mic_recorder(
                        start_prompt="🎤 Record",
                        stop_prompt="⏹️ Stop",
                        just_once=False,
                        use_container_width=True,
                        key="edit_next_voice"
                    )
                    
                    if edit_next_audio:
                        transcribed = transcribe_audio(edit_next_audio['bytes'])
                        if transcribed:
                            st.text_area("Transcribed:", value=transcribed, height=80, key="edit_next_transcribed")

def render_project_creator():
    """Render new project creation interface"""
    st.header("➕ Create New Project")
    
    # Show voice input availability
    if MIC_RECORDER_AVAILABLE:
        st.info("🎤 Voice input is enabled! Click the microphone button next to any field to use voice-to-text.")
    else:
        st.warning("🎤 Voice input is not available. Install streamlit-mic-recorder for voice input functionality.")
    
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            parent_dir = st.text_input("Parent Directory", value="", help="e.g., 'personal', 'work', 'B2L'")
            project_name = st.text_input("Project Name", value="", help="e.g., 'platform', 'mobile_app'")
        
        with col2:
            st.markdown("**Project Structure Preview:**")
            if parent_dir and project_name:
                st.code(f"projects/{parent_dir}/{project_name}/\n├── goal.md\n├── completed.md\n└── next.md")
        
        st.markdown("---")
        
        # Use the voice input fields
        st.markdown("### 🎯 Project Goal")
        st.markdown("*Describe the main objective and requirements of your project*")
        goal = st.text_area(
            "Project Goal",
            height=200,
            help="Describe the main objective and requirements of your project",
            key="goal_text",
            label_visibility="collapsed"
        )
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("### ✅ Completed Tasks")
            st.markdown("*List what has already been accomplished*")
            completed = st.text_area(
                "Completed Tasks",
                height=150,
                help="List what has already been accomplished",
                key="completed_text",
                label_visibility="collapsed"
            )
        
        with col4:
            st.markdown("### 📝 Next Steps")
            st.markdown("*Define the immediate next actions to take*")
            next_steps = st.text_area(
                "Next Steps",
                height=150,
                help="Define the immediate next actions to take",
                key="next_steps_text",
                label_visibility="collapsed"
            )
        
        submitted = st.form_submit_button("🚀 Create Project", type="primary")
        
        if submitted:
            if not all([parent_dir, project_name, goal]):
                st.error("Please fill in Parent Directory, Project Name, and Goal fields.")
            else:
                project_manager = ProjectManager()
                success = project_manager.create_project(
                    name=project_name,
                    parent_dir=parent_dir,
                    goal=goal,
                    completed=completed,
                    next_steps=next_steps
                )
                
                if success:
                    st.success(f"✅ Project '{parent_dir}/{project_name}' created successfully!")
                    st.balloons()
                    st.rerun()
    
    # Voice input section outside the form for better UX
    if MIC_RECORDER_AVAILABLE:
        st.markdown("---")
        st.markdown("### 🎤 Voice Input Helper")
        st.markdown("Use the sections below to record voice input, then copy the transcribed text to the form above.")
        
        voice_col1, voice_col2, voice_col3 = st.columns(3)
        
        with voice_col1:
            st.markdown("**🎯 Goal Voice Input**")
            goal_audio = mic_recorder(
                start_prompt="🎤 Record Goal",
                stop_prompt="⏹️ Stop",
                just_once=False,
                use_container_width=True,
                key="goal_voice"
            )
            
            if goal_audio:
                transcribed = transcribe_audio(goal_audio['bytes'])
                if transcribed:
                    st.text_area("Transcribed Goal:", value=transcribed, height=100, key="goal_transcribed")
        
        with voice_col2:
            st.markdown("**✅ Completed Tasks Voice Input**")
            completed_audio = mic_recorder(
                start_prompt="🎤 Record Completed",
                stop_prompt="⏹️ Stop",
                just_once=False,
                use_container_width=True,
                key="completed_voice"
            )
            
            if completed_audio:
                transcribed = transcribe_audio(completed_audio['bytes'])
                if transcribed:
                    st.text_area("Transcribed Completed:", value=transcribed, height=100, key="completed_transcribed")
        
        with voice_col3:
            st.markdown("**📝 Next Steps Voice Input**")
            next_audio = mic_recorder(
                start_prompt="🎤 Record Next Steps",
                stop_prompt="⏹️ Stop",
                just_once=False,
                use_container_width=True,
                key="next_voice"
            )
            
            if next_audio:
                transcribed = transcribe_audio(next_audio['bytes'])
                if transcribed:
                    st.text_area("Transcribed Next Steps:", value=transcribed, height=100, key="next_transcribed")

def main():
    st.title("🎯 AI Goal Compass")
    st.markdown("*Intelligent Project Analysis & Management System*")
    
    # Initialize components
    project_manager = ProjectManager()
    analyzer = ProjectAnalyzer()
    
    # Load projects
    projects = project_manager.scan_projects()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    page = st.sidebar.radio(
        "Choose a section:",
        ["📊 Overview", "🔍 Analysis", "➕ Create Project", "⚙️ Settings"]
    )
    
    # Main content
    if page == "📊 Overview":
        render_project_overview(projects)
    
    elif page == "🔍 Analysis":
        render_project_analyzer(projects, analyzer)
    
    elif page == "➕ Create Project":
        render_project_creator()
    
    elif page == "⚙️ Settings":
        st.header("⚙️ Settings")
        
        st.subheader("🤖 Ollama Configuration")
        st.info("Make sure Ollama is running locally with the llama3.2 model installed.")
        st.code("ollama pull llama3.2")
        
        st.subheader("📁 Projects Directory")
        st.text(f"Current: {project_manager.projects_dir.absolute()}")
        
        if st.button("🔄 Refresh Projects"):
            st.rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Tips:**")
    st.sidebar.markdown("• Ensure Ollama is running")
    st.sidebar.markdown("• Use clear, detailed project goals")
    st.sidebar.markdown("• Update completed tasks regularly")
    
    if MIC_RECORDER_AVAILABLE:
        st.sidebar.markdown("• 🎤 Voice input is available!")
        st.sidebar.markdown("• Click microphone buttons to record")
    else:
        st.sidebar.markdown("• ℹ️ Install streamlit-mic-recorder for voice input")

if __name__ == "__main__":
    main()
