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

# CrewAI and Ollama imports
from crewai import Agent, Task, Crew, Process
from langchain_ollama import OllamaLLM

# Set page config
st.set_page_config(
    page_title="AI Goal Compass - Project Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        
        tab1, tab2, tab3 = st.tabs(["📖 Project Details", "🤖 AI Analysis", "📊 Visual Flow"])
        
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

def render_project_creator():
    """Render new project creation interface"""
    st.header("➕ Create New Project")
    
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            parent_dir = st.text_input("Parent Directory", value="", help="e.g., 'personal', 'work', 'B2L'")
            project_name = st.text_input("Project Name", value="", help="e.g., 'platform', 'mobile_app'")
        
        with col2:
            st.markdown("**Project Structure Preview:**")
            if parent_dir and project_name:
                st.code(f"projects/{parent_dir}/{project_name}/\n├── goal.md\n├── completed.md\n└── next.md")
        
        goal = st.text_area(
            "🎯 Project Goal",
            height=200,
            help="Describe the main objective and requirements of your project"
        )
        
        col3, col4 = st.columns(2)
        
        with col3:
            completed = st.text_area(
                "✅ Completed Tasks",
                height=150,
                help="List what has already been accomplished"
            )
        
        with col4:
            next_steps = st.text_area(
                "📝 Next Steps",
                height=150,
                help="Define the immediate next actions to take"
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

if __name__ == "__main__":
    main()
