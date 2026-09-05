import os
import sqlite3
import time
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# GEMINI IMPORT
# ============================================================

try:
    from google import genai
except ImportError:
    genai = None


# ============================================================
# FLASK CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "career_guidance.db")

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret-key"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)


# ============================================================
# CAREER DIRECTORY
# ============================================================

CAREERS = [

    {
        "title": "Web Developer",
        "icon": "🌐",
        "demand": "High Demand",
        "skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Python",
            "Git"
        ],
        "salary": "₹3–15 LPA+",
        "description": "Build websites and web applications for businesses, startups and users.",
        "overview": "Web developers create and maintain websites and web applications. You can start with frontend development and later move into backend or full-stack development.",
        "what_you_do": "Build responsive websites, create user interfaces, develop APIs, connect databases and deploy web applications.",
        "tools": [
            "VS Code",
            "Git",
            "GitHub",
            "React",
            "Node.js",
            "Flask"
        ],
        "beginner_projects": [
            "Personal Portfolio",
            "To-Do App",
            "Weather App"
        ],
        "advanced_projects": [
            "E-commerce Website",
            "Real-time Chat Application",
            "Full-stack SaaS Application"
        ],
        "suitable_for": "Students who enjoy coding, websites and creating things that people can use.",
        "future_scope": "Strong opportunities in frontend, backend, full-stack, cloud and AI-powered web development."
    },

    {
        "title": "Software Engineer",
        "icon": "💻",
        "demand": "Very High Demand",
        "skills": [
            "Python",
            "Java",
            "C++",
            "Data Structures",
            "Algorithms",
            "Git"
        ],
        "salary": "₹4–25 LPA+",
        "description": "Design, develop, test and maintain software applications and systems.",
        "overview": "Software engineering focuses on solving problems with reliable and scalable software. It is one of the broadest technology career paths.",
        "what_you_do": "Write production code, design software systems, debug applications, review code and work with development teams.",
        "tools": [
            "Git",
            "GitHub",
            "VS Code",
            "Docker",
            "Linux",
            "Cloud Platforms"
        ],
        "beginner_projects": [
            "Calculator Application",
            "Student Management System",
            "Expense Tracker"
        ],
        "advanced_projects": [
            "Scalable Web Platform",
            "Distributed System",
            "Microservices Application"
        ],
        "suitable_for": "People who enjoy logical problem solving, programming and building software systems.",
        "future_scope": "Excellent long-term scope across software products, cloud, AI, fintech, cybersecurity and enterprise technology."
    },

    {
        "title": "Data Analyst",
        "icon": "📊",
        "demand": "High Demand",
        "skills": [
            "Excel",
            "SQL",
            "Python",
            "Pandas",
            "Statistics",
            "Power BI"
        ],
        "salary": "₹3–12 LPA+",
        "description": "Turn raw data into useful insights that help organizations make better decisions.",
        "overview": "Data analysts collect, clean, analyze and visualize data to answer business questions.",
        "what_you_do": "Clean datasets, write SQL queries, create dashboards, analyze trends and communicate insights.",
        "tools": [
            "Excel",
            "SQL",
            "Power BI",
            "Tableau",
            "Python",
            "Pandas"
        ],
        "beginner_projects": [
            "Sales Dashboard",
            "Movie Dataset Analysis",
            "Student Performance Analysis"
        ],
        "advanced_projects": [
            "Business Intelligence Dashboard",
            "Customer Churn Analysis",
            "Automated Analytics Pipeline"
        ],
        "suitable_for": "Students who enjoy numbers, analysis, business problems and visualization.",
        "future_scope": "Can grow into senior analyst, business analyst, analytics engineer or data scientist roles."
    },

    {
        "title": "Data Scientist",
        "icon": "📈",
        "demand": "Very High Demand",
        "skills": [
            "Python",
            "SQL",
            "Statistics",
            "Machine Learning",
            "Pandas",
            "Data Visualization"
        ],
        "salary": "₹5–25 LPA+",
        "description": "Use data, statistics and machine learning to solve complex real-world problems.",
        "overview": "Data scientists combine programming, statistics and machine learning to extract valuable patterns from data.",
        "what_you_do": "Analyze datasets, build predictive models, perform experiments and communicate data-driven findings.",
        "tools": [
            "Python",
            "Jupyter",
            "Pandas",
            "NumPy",
            "Scikit-learn",
            "Power BI"
        ],
        "beginner_projects": [
            "House Price Prediction",
            "Customer Segmentation",
            "Sales Data Analysis"
        ],
        "advanced_projects": [
            "Recommendation System",
            "Fraud Detection Model",
            "End-to-end ML Analytics Platform"
        ],
        "suitable_for": "People interested in mathematics, statistics, programming and solving problems using data.",
        "future_scope": "Strong opportunities in AI, machine learning, analytics, fintech, healthcare and research."
    },

    {
        "title": "Machine Learning Engineer",
        "icon": "🤖",
        "demand": "Very High Demand",
        "skills": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "SQL",
            "APIs",
            "MLOps"
        ],
        "salary": "₹6–30 LPA+",
        "description": "Build, train, deploy and maintain machine learning systems.",
        "overview": "Machine learning engineers turn ML models into reliable production systems that can serve real users.",
        "what_you_do": "Prepare data, train models, optimize performance, build inference APIs and deploy ML systems.",
        "tools": [
            "Python",
            "Scikit-learn",
            "PyTorch",
            "TensorFlow",
            "Docker",
            "MLflow"
        ],
        "beginner_projects": [
            "Spam Classifier",
            "House Price Predictor",
            "Image Classification Model"
        ],
        "advanced_projects": [
            "Recommendation Engine",
            "Real-time Fraud Detection",
            "Production ML Platform"
        ],
        "suitable_for": "Students who enjoy coding, mathematics, AI and building intelligent applications.",
        "future_scope": "Excellent growth through AI engineering, deep learning, MLOps and generative AI."
    },

    {
        "title": "Generative AI Engineer",
        "icon": "✨",
        "demand": "Rapidly Growing",
        "skills": [
            "Python",
            "LLMs",
            "Prompt Engineering",
            "RAG",
            "APIs",
            "Vector Databases"
        ],
        "salary": "₹6–35 LPA+",
        "description": "Build applications powered by large language models and generative AI.",
        "overview": "Generative AI engineers build practical applications using language, vision, audio and multimodal AI models.",
        "what_you_do": "Integrate AI APIs, build RAG systems, create agents, evaluate models and deploy AI applications.",
        "tools": [
            "Python",
            "Gemini API",
            "OpenAI APIs",
            "LangChain",
            "Vector Databases",
            "Docker"
        ],
        "beginner_projects": [
            "AI Chatbot",
            "PDF Question Answering App",
            "AI Resume Assistant"
        ],
        "advanced_projects": [
            "RAG Knowledge Platform",
            "AI Agent System",
            "Multi-modal AI Application"
        ],
        "suitable_for": "People interested in AI who want to quickly build useful real-world applications.",
        "future_scope": "Rapid growth across AI products, automation, enterprise software, education and developer tools."
    },

    {
        "title": "AI Research Scientist",
        "icon": "🧠",
        "demand": "Specialized",
        "skills": [
            "Python",
            "Mathematics",
            "Statistics",
            "Deep Learning",
            "Research",
            "Algorithms"
        ],
        "salary": "₹8–40 LPA+",
        "description": "Research new artificial intelligence methods, algorithms and machine learning techniques.",
        "overview": "AI research scientists work on advancing the capabilities of artificial intelligence through experiments and new algorithms.",
        "what_you_do": "Read research papers, design experiments, train models, evaluate results and publish research.",
        "tools": [
            "Python",
            "PyTorch",
            "TensorFlow",
            "Jupyter",
            "Linux",
            "GPU Computing"
        ],
        "beginner_projects": [
            "Neural Network From Scratch",
            "Image Classifier",
            "ML Paper Reimplementation"
        ],
        "advanced_projects": [
            "Novel ML Architecture",
            "LLM Research Project",
            "AI Research Publication"
        ],
        "suitable_for": "Students deeply interested in mathematics, algorithms, AI research and experimentation.",
        "future_scope": "Opportunities in research labs, universities, advanced AI companies and R&D teams."
    },

    {
        "title": "Cybersecurity Analyst",
        "icon": "🔐",
        "demand": "High Demand",
        "skills": [
            "Networking",
            "Linux",
            "Security",
            "Python",
            "SIEM",
            "Incident Response"
        ],
        "salary": "₹4–18 LPA+",
        "description": "Protect systems, networks and organizations from cyber threats.",
        "overview": "Cybersecurity analysts monitor systems, investigate suspicious activity and help organizations reduce security risks.",
        "what_you_do": "Monitor logs, investigate incidents, analyze vulnerabilities and implement security controls.",
        "tools": [
            "Linux",
            "Wireshark",
            "SIEM",
            "Nmap",
            "Python",
            "Security Platforms"
        ],
        "beginner_projects": [
            "Network Monitoring Lab",
            "Log Analysis Dashboard",
            "Security Awareness Website"
        ],
        "advanced_projects": [
            "SOC Monitoring Platform",
            "Threat Detection System",
            "Security Automation Tool"
        ],
        "suitable_for": "People interested in computers, networking, investigation and digital security.",
        "future_scope": "Can progress into SOC, incident response, threat intelligence, security engineering and leadership."
    },

    {
        "title": "Ethical Hacker",
        "icon": "🛡️",
        "demand": "High Demand",
        "skills": [
            "Networking",
            "Linux",
            "Web Security",
            "Python",
            "Security Testing",
            "OWASP"
        ],
        "salary": "₹4–20 LPA+",
        "description": "Authorized security professionals who identify and help fix vulnerabilities.",
        "overview": "Ethical hackers perform authorized security assessments to identify weaknesses before malicious attackers can exploit them.",
        "what_you_do": "Perform authorized security testing, document findings and help development teams improve security.",
        "tools": [
            "Kali Linux",
            "Burp Suite",
            "Wireshark",
            "Nmap",
            "OWASP Tools",
            "Python"
        ],
        "beginner_projects": [
            "Cybersecurity Lab",
            "Web Security Learning Lab",
            "Network Analysis Project"
        ],
        "advanced_projects": [
            "Security Assessment Platform",
            "Vulnerability Management Dashboard",
            "Automated Security Testing Tool"
        ],
        "suitable_for": "People who enjoy cybersecurity, networking, investigation and technical problem solving.",
        "future_scope": "Can lead to penetration testing, application security, red teaming and security engineering."
    },

    {
        "title": "Cloud Engineer",
        "icon": "☁️",
        "demand": "Very High Demand",
        "skills": [
            "Linux",
            "Networking",
            "AWS",
            "Azure",
            "Docker",
            "Terraform"
        ],
        "salary": "₹5–22 LPA+",
        "description": "Design, deploy and manage applications and infrastructure in the cloud.",
        "overview": "Cloud engineers manage scalable computing infrastructure and help organizations move applications to cloud platforms.",
        "what_you_do": "Deploy servers, configure networks, manage cloud services and automate infrastructure.",
        "tools": [
            "AWS",
            "Azure",
            "Docker",
            "Terraform",
            "Linux",
            "Kubernetes"
        ],
        "beginner_projects": [
            "Cloud-hosted Portfolio",
            "Static Website Deployment",
            "Cloud Storage Application"
        ],
        "advanced_projects": [
            "Scalable Cloud Architecture",
            "Serverless Application",
            "Multi-service Cloud Platform"
        ],
        "suitable_for": "Students interested in infrastructure, cloud platforms, networking and automation.",
        "future_scope": "Strong demand across cloud architecture, DevOps, platform engineering and infrastructure."
    },

    {
        "title": "DevOps Engineer",
        "icon": "⚙️",
        "demand": "Very High Demand",
        "skills": [
            "Linux",
            "Git",
            "Docker",
            "CI/CD",
            "Kubernetes",
            "Cloud"
        ],
        "salary": "₹5–25 LPA+",
        "description": "Automate software delivery and improve reliability between development and operations.",
        "overview": "DevOps engineers build systems and processes that allow teams to develop, test and deploy software efficiently.",
        "what_you_do": "Create CI/CD pipelines, automate infrastructure, monitor applications and manage deployments.",
        "tools": [
            "GitHub Actions",
            "Docker",
            "Kubernetes",
            "Jenkins",
            "Terraform",
            "AWS"
        ],
        "beginner_projects": [
            "CI/CD Pipeline",
            "Dockerized Flask App",
            "Automated Deployment"
        ],
        "advanced_projects": [
            "Kubernetes Platform",
            "Infrastructure-as-Code System",
            "Complete DevOps Pipeline"
        ],
        "suitable_for": "People interested in automation, infrastructure, cloud and improving development workflows.",
        "future_scope": "Strong progression toward platform engineering, cloud engineering and SRE."
    },

    {
        "title": "UI/UX Designer",
        "icon": "🎨",
        "demand": "High Demand",
        "skills": [
            "Figma",
            "UI Design",
            "UX Research",
            "Wireframing",
            "Prototyping",
            "Design Systems"
        ],
        "salary": "₹3–18 LPA+",
        "description": "Design intuitive, attractive and user-friendly digital experiences.",
        "overview": "UI/UX designers research users and create interfaces that are useful, accessible and visually appealing.",
        "what_you_do": "Research users, create wireframes, design interfaces, prototype interactions and test experiences.",
        "tools": [
            "Figma",
            "FigJam",
            "Adobe XD",
            "Photoshop",
            "Design Systems"
        ],
        "beginner_projects": [
            "Mobile App Redesign",
            "Landing Page Design",
            "Portfolio Website Design"
        ],
        "advanced_projects": [
            "Complete Product Design",
            "Design System",
            "UX Research Case Study"
        ],
        "suitable_for": "Creative people interested in design, psychology, technology and user experiences.",
        "future_scope": "Opportunities in product design, UX research, interaction design and design leadership."
    },

    {
        "title": "Mobile App Developer",
        "icon": "📱",
        "demand": "High Demand",
        "skills": [
            "Flutter",
            "React Native",
            "Kotlin",
            "Swift",
            "APIs",
            "UI Design"
        ],
        "salary": "₹4–18 LPA+",
        "description": "Create mobile applications for Android and iOS devices.",
        "overview": "Mobile developers build applications that run on smartphones and tablets.",
        "what_you_do": "Build interfaces, connect APIs, manage app state, test applications and publish mobile apps.",
        "tools": [
            "Flutter",
            "Dart",
            "Android Studio",
            "Firebase",
            "React Native"
        ],
        "beginner_projects": [
            "To-Do Mobile App",
            "Weather App",
            "Expense Tracker"
        ],
        "advanced_projects": [
            "Social Media App",
            "Food Delivery App",
            "Real-time Collaboration App"
        ],
        "suitable_for": "Students who enjoy app development and want to build products for mobile users.",
        "future_scope": "Strong opportunities in Android, iOS, cross-platform development and mobile product engineering."
    },

    {
        "title": "Database Administrator",
        "icon": "🗄️",
        "demand": "High Demand",
        "skills": [
            "SQL",
            "Database Design",
            "Linux",
            "Backup",
            "Security",
            "Performance"
        ],
        "salary": "₹4–18 LPA+",
        "description": "Manage databases, data availability, security and performance.",
        "overview": "Database administrators ensure that organizational data remains secure, available and performant.",
        "what_you_do": "Manage databases, backups, permissions, performance monitoring and recovery procedures.",
        "tools": [
            "MySQL",
            "PostgreSQL",
            "MongoDB",
            "SQL Server",
            "Linux"
        ],
        "beginner_projects": [
            "Student Database",
            "Library Management Database",
            "SQL Reporting System"
        ],
        "advanced_projects": [
            "High Availability Database",
            "Database Monitoring System",
            "Backup and Recovery Platform"
        ],
        "suitable_for": "People interested in data organization, SQL, infrastructure and system reliability.",
        "future_scope": "Can grow into database engineering, cloud database administration and data architecture."
    },

    {
        "title": "Blockchain Developer",
        "icon": "⛓️",
        "demand": "Growing",
        "skills": [
            "JavaScript",
            "Solidity",
            "Cryptography",
            "Smart Contracts",
            "Web3",
            "Blockchain"
        ],
        "salary": "₹5–25 LPA+",
        "description": "Build decentralized applications and blockchain-based systems.",
        "overview": "Blockchain developers create applications and smart contracts that operate on decentralized networks.",
        "what_you_do": "Develop smart contracts, build decentralized applications and interact with blockchain networks.",
        "tools": [
            "Solidity",
            "Ethereum",
            "Hardhat",
            "JavaScript",
            "Web3 Libraries"
        ],
        "beginner_projects": [
            "Simple Smart Contract",
            "Blockchain Explorer UI",
            "Decentralized Voting Demo"
        ],
        "advanced_projects": [
            "DeFi Application",
            "NFT Platform",
            "Decentralized Application"
        ],
        "suitable_for": "Developers interested in decentralized systems, cryptography and emerging technologies.",
        "future_scope": "Opportunities in Web3 infrastructure, smart contracts, decentralized applications and blockchain engineering."
    },

    {
        "title": "Game Developer",
        "icon": "🎮",
        "demand": "Growing",
        "skills": [
            "C#",
            "C++",
            "Game Design",
            "3D Math",
            "Unity",
            "Unreal Engine"
        ],
        "salary": "₹3–18 LPA+",
        "description": "Design and develop interactive video games and gaming experiences.",
        "overview": "Game developers combine programming, art, physics and design to create interactive games.",
        "what_you_do": "Program gameplay, physics, controls, graphics systems and multiplayer functionality.",
        "tools": [
            "Unity",
            "Unreal Engine",
            "C#",
            "C++",
            "Blender"
        ],
        "beginner_projects": [
            "2D Platformer",
            "Puzzle Game",
            "Simple Mobile Game"
        ],
        "advanced_projects": [
            "3D Multiplayer Game",
            "Open World Prototype",
            "Game AI System"
        ],
        "suitable_for": "Creative programmers who enjoy games, storytelling, graphics and interactive experiences.",
        "future_scope": "Opportunities in mobile gaming, PC/console games, VR/AR and interactive media."
    },

    {
        "title": "Product Manager",
        "icon": "🚀",
        "demand": "High Demand",
        "skills": [
            "Product Strategy",
            "Communication",
            "Analytics",
            "UX",
            "Agile",
            "Leadership"
        ],
        "salary": "₹6–30 LPA+",
        "description": "Plan products, understand users and coordinate teams to build useful solutions.",
        "overview": "Product managers connect business goals, user needs and technology to guide products from idea to launch.",
        "what_you_do": "Research users, define product requirements, prioritize features, analyze metrics and coordinate teams.",
        "tools": [
            "Jira",
            "Notion",
            "Figma",
            "Google Analytics",
            "Product Analytics Tools"
        ],
        "beginner_projects": [
            "Product Case Study",
            "App Feature Analysis",
            "Product Roadmap"
        ],
        "advanced_projects": [
            "Complete Product Strategy",
            "Growth Experiment Plan",
            "Product Launch Case Study"
        ],
        "suitable_for": "People who enjoy technology, business, communication, strategy and solving user problems.",
        "future_scope": "Can progress toward senior product management, product leadership and startup roles."
    }
]


# ============================================================
# CAREER ROADMAPS
# ============================================================

ROADMAPS = {

    "Web Developer": [
        "Stage 1 — Learn HTML fundamentals",
        "Stage 2 — Learn CSS and responsive design",
        "Stage 3 — Learn JavaScript fundamentals",
        "Stage 4 — Learn DOM and browser APIs",
        "Stage 5 — Learn Git and GitHub",
        "Stage 6 — Learn frontend frameworks such as React",
        "Stage 7 — Learn backend development",
        "Stage 8 — Learn REST APIs and databases",
        "Stage 9 — Build full-stack projects",
        "Stage 10 — Learn authentication and security",
        "Stage 11 — Deploy projects to the cloud",
        "Stage 12 — Build a strong portfolio and apply for jobs"
    ],

    "Software Engineer": [
        "Stage 1 — Learn programming fundamentals",
        "Stage 2 — Master one programming language",
        "Stage 3 — Learn Data Structures",
        "Stage 4 — Learn Algorithms",
        "Stage 5 — Learn Object-Oriented Programming",
        "Stage 6 — Learn Git and software development workflows",
        "Stage 7 — Learn databases and SQL",
        "Stage 8 — Learn APIs and backend development",
        "Stage 9 — Learn testing and debugging",
        "Stage 10 — Learn system design fundamentals",
        "Stage 11 — Build production-quality projects",
        "Stage 12 — Prepare for technical interviews and jobs"
    ],

    "Data Analyst": [
        "Stage 1 — Learn Excel fundamentals",
        "Stage 2 — Learn SQL basics",
        "Stage 3 — Learn advanced SQL",
        "Stage 4 — Learn statistics fundamentals",
        "Stage 5 — Learn Python basics",
        "Stage 6 — Learn NumPy and Pandas",
        "Stage 7 — Learn data cleaning",
        "Stage 8 — Learn Power BI or Tableau",
        "Stage 9 — Build analytics dashboards",
        "Stage 10 — Solve real business datasets",
        "Stage 11 — Create a data portfolio",
        "Stage 12 — Prepare for analyst interviews"
    ],

    "Data Scientist": [
        "Stage 1 — Learn Python",
        "Stage 2 — Learn NumPy and Pandas",
        "Stage 3 — Learn statistics",
        "Stage 4 — Learn data visualization",
        "Stage 5 — Learn SQL",
        "Stage 6 — Learn machine learning fundamentals",
        "Stage 7 — Learn Scikit-learn",
        "Stage 8 — Build predictive models",
        "Stage 9 — Learn feature engineering",
        "Stage 10 — Learn model evaluation",
        "Stage 11 — Build end-to-end projects",
        "Stage 12 — Build portfolio and prepare for interviews"
    ],

    "Machine Learning Engineer": [
        "Stage 1 — Master Python",
        "Stage 2 — Learn mathematics and statistics",
        "Stage 3 — Learn machine learning fundamentals",
        "Stage 4 — Learn Scikit-learn",
        "Stage 5 — Learn deep learning",
        "Stage 6 — Learn PyTorch or TensorFlow",
        "Stage 7 — Learn model deployment",
        "Stage 8 — Learn APIs and Docker",
        "Stage 9 — Learn MLOps fundamentals",
        "Stage 10 — Build production ML projects",
        "Stage 11 — Deploy ML systems",
        "Stage 12 — Prepare portfolio and interviews"
    ],

    "Generative AI Engineer": [
        "Stage 1 — Learn Python fundamentals",
        "Stage 2 — Understand machine learning basics",
        "Stage 3 — Learn LLM fundamentals",
        "Stage 4 — Learn prompt engineering",
        "Stage 5 — Learn AI APIs",
        "Stage 6 — Learn embeddings",
        "Stage 7 — Learn vector databases",
        "Stage 8 — Build RAG applications",
        "Stage 9 — Learn AI agents",
        "Stage 10 — Learn evaluation and safety",
        "Stage 11 — Deploy AI applications",
        "Stage 12 — Build an AI portfolio"
    ],

    "AI Research Scientist": [
        "Stage 1 — Master Python",
        "Stage 2 — Learn linear algebra",
        "Stage 3 — Learn probability and statistics",
        "Stage 4 — Learn machine learning",
        "Stage 5 — Learn deep learning",
        "Stage 6 — Learn PyTorch",
        "Stage 7 — Study research papers",
        "Stage 8 — Reproduce published experiments",
        "Stage 9 — Design original experiments",
        "Stage 10 — Learn research methodology",
        "Stage 11 — Write technical papers",
        "Stage 12 — Build research portfolio"
    ],

    "Cybersecurity Analyst": [
        "Stage 1 — Learn computer fundamentals",
        "Stage 2 — Learn networking fundamentals",
        "Stage 3 — Learn Linux",
        "Stage 4 — Learn cybersecurity fundamentals",
        "Stage 5 — Learn common security threats",
        "Stage 6 — Learn log analysis",
        "Stage 7 — Learn SIEM concepts",
        "Stage 8 — Learn incident response",
        "Stage 9 — Build a security lab",
        "Stage 10 — Practice defensive security",
        "Stage 11 — Build cybersecurity projects",
        "Stage 12 — Prepare for security roles"
    ],

    "Ethical Hacker": [
        "Stage 1 — Learn computer networking",
        "Stage 2 — Learn Linux",
        "Stage 3 — Learn web technologies",
        "Stage 4 — Learn cybersecurity fundamentals",
        "Stage 5 — Study OWASP concepts",
        "Stage 6 — Learn security testing methodology",
        "Stage 7 — Practice in legal training labs",
        "Stage 8 — Learn vulnerability assessment",
        "Stage 9 — Learn security reporting",
        "Stage 10 — Build authorized security projects",
        "Stage 11 — Develop a cybersecurity portfolio",
        "Stage 12 — Prepare for security careers"
    ],

    "Cloud Engineer": [
        "Stage 1 — Learn Linux",
        "Stage 2 — Learn networking",
        "Stage 3 — Learn cloud fundamentals",
        "Stage 4 — Learn AWS or Azure",
        "Stage 5 — Learn cloud storage and compute",
        "Stage 6 — Learn cloud networking",
        "Stage 7 — Learn Docker",
        "Stage 8 — Learn infrastructure automation",
        "Stage 9 — Learn Terraform",
        "Stage 10 — Learn Kubernetes basics",
        "Stage 11 — Deploy scalable applications",
        "Stage 12 — Build cloud portfolio"
    ],

    "DevOps Engineer": [
        "Stage 1 — Learn Linux",
        "Stage 2 — Learn Git",
        "Stage 3 — Learn networking basics",
        "Stage 4 — Learn Docker",
        "Stage 5 — Learn CI/CD",
        "Stage 6 — Learn GitHub Actions or Jenkins",
        "Stage 7 — Learn cloud fundamentals",
        "Stage 8 — Learn Infrastructure as Code",
        "Stage 9 — Learn Terraform",
        "Stage 10 — Learn Kubernetes",
        "Stage 11 — Learn monitoring and logging",
        "Stage 12 — Build a complete DevOps project"
    ],

    "UI/UX Designer": [
        "Stage 1 — Learn design fundamentals",
        "Stage 2 — Learn typography and color",
        "Stage 3 — Learn UX principles",
        "Stage 4 — Learn user research",
        "Stage 5 — Create user personas",
        "Stage 6 — Learn wireframing",
        "Stage 7 — Learn Figma",
        "Stage 8 — Create interactive prototypes",
        "Stage 9 — Conduct usability testing",
        "Stage 10 — Build design systems",
        "Stage 11 — Create case studies",
        "Stage 12 — Build a professional design portfolio"
    ],

    "Mobile App Developer": [
        "Stage 1 — Learn programming fundamentals",
        "Stage 2 — Choose Flutter, React Native, Kotlin or Swift",
        "Stage 3 — Learn mobile UI development",
        "Stage 4 — Learn navigation and state management",
        "Stage 5 — Learn APIs",
        "Stage 6 — Learn local storage",
        "Stage 7 — Learn authentication",
        "Stage 8 — Learn Firebase or backend services",
        "Stage 9 — Build complete mobile applications",
        "Stage 10 — Learn testing",
        "Stage 11 — Publish an application",
        "Stage 12 — Build a mobile development portfolio"
    ],

    "Database Administrator": [
        "Stage 1 — Learn database fundamentals",
        "Stage 2 — Learn SQL",
        "Stage 3 — Learn relational databases",
        "Stage 4 — Learn database design",
        "Stage 5 — Learn indexing",
        "Stage 6 — Learn database security",
        "Stage 7 — Learn backup and recovery",
        "Stage 8 — Learn performance tuning",
        "Stage 9 — Learn replication",
        "Stage 10 — Learn cloud databases",
        "Stage 11 — Build database administration projects",
        "Stage 12 — Prepare for database roles"
    ],

    "Blockchain Developer": [
        "Stage 1 — Learn programming fundamentals",
        "Stage 2 — Learn JavaScript",
        "Stage 3 — Understand blockchain concepts",
        "Stage 4 — Learn cryptography fundamentals",
        "Stage 5 — Learn Ethereum concepts",
        "Stage 6 — Learn Solidity",
        "Stage 7 — Build smart contracts",
        "Stage 8 — Learn Web3 development",
        "Stage 9 — Build decentralized applications",
        "Stage 10 — Learn smart contract testing",
        "Stage 11 — Build blockchain projects",
        "Stage 12 — Create a Web3 portfolio"
    ],

    "Game Developer": [
        "Stage 1 — Learn programming fundamentals",
        "Stage 2 — Learn C# or C++",
        "Stage 3 — Learn game mathematics",
        "Stage 4 — Learn Unity or Unreal Engine",
        "Stage 5 — Learn game physics",
        "Stage 6 — Learn game UI",
        "Stage 7 — Build a 2D game",
        "Stage 8 — Learn 3D development",
        "Stage 9 — Learn animation and audio",
        "Stage 10 — Learn multiplayer concepts",
        "Stage 11 — Build a complete game",
        "Stage 12 — Build a game development portfolio"
    ],

    "Product Manager": [
        "Stage 1 — Understand product management",
        "Stage 2 — Learn user research",
        "Stage 3 — Learn product discovery",
        "Stage 4 — Learn market research",
        "Stage 5 — Learn product strategy",
        "Stage 6 — Learn product roadmapping",
        "Stage 7 — Learn UX fundamentals",
        "Stage 8 — Learn product analytics",
        "Stage 9 — Learn Agile and Scrum",
        "Stage 10 — Practice prioritization",
        "Stage 11 — Build product case studies",
        "Stage 12 — Prepare for product management interviews"
    ]
}


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # CHATS TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # ========================================================
    # DATABASE MIGRATION FIX
    # ========================================================
    #
    # Your old database may have been created with
    # "password_hash" instead of "password".
    #
    # The login error:
    #
    # IndexError: No item with that key
    #
    # happens when user["password"] does not exist.
    #
    # This code automatically fixes that old database.
    # ========================================================

    columns = conn.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    # If password column does not exist
    if "password" not in column_names:

        # If old database has password_hash,
        # copy its values into the new password column.
        if "password_hash" in column_names:

            conn.execute(
                "ALTER TABLE users ADD COLUMN password TEXT"
            )

            conn.execute("""
                UPDATE users
                SET password = password_hash
                WHERE password IS NULL
            """)

        else:

            # Otherwise simply add password column.
            conn.execute(
                "ALTER TABLE users ADD COLUMN password TEXT"
            )

    conn.commit()
    conn.close()


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


# ============================================================
# GEMINI AI
# ============================================================

def ai_reply(message, history=None):

    if not GEMINI_API_KEY:
        return (
            "Demo mode: Gemini API is not configured yet. "
            "Please add GEMINI_API_KEY to your .env file."
        )

    if genai is None:
        return (
            "Gemini package is not installed. "
            "Please install the required packages from requirements.txt."
        )

    history = history or []

    history_text = ""

    for item in history[-8:]:

        role = item.get("role", "user")
        text = item.get("message", "")

        history_text += f"{role}: {text}\n"

    prompt = f"""
You are CareerGuide AI, a friendly and practical career guidance assistant.

Your job is to help students and professionals understand careers,
skills, learning paths, projects and job preparation.

Focus on practical advice and keep the answer easy to understand.

The user may ask about:

- Career selection
- Skills
- Roadmaps
- Projects
- AI
- Software development
- Data
- Cybersecurity
- Cloud
- Design
- Product management
- Interview preparation

When recommending a career, explain:

1. Why it may fit
2. Skills to learn
3. Beginner projects
4. A practical 30/60/90-day plan

Do not guarantee jobs, salaries or employment outcomes.

Previous conversation:

{history_text}

Current user question:

{message}

Give a helpful, structured answer.
"""

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    models_to_try = [
        GEMINI_MODEL,
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-3.7-flash"
    ]

    # Remove duplicates
    unique_models = []

    for model in models_to_try:

        if model and model not in unique_models:
            unique_models.append(model)

    for model in unique_models:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response and response.text:
                    return response.text

                return (
                    "I couldn't generate a response right now. "
                    "Please try again."
                )

            except Exception as exc:

                error_text = str(exc).lower()

                temporary_error = any(
                    keyword in error_text
                    for keyword in [
                        "503",
                        "unavailable",
                        "429",
                        "resource exhausted",
                        "overloaded",
                        "temporarily",
                        "service unavailable"
                    ]
                )

                if temporary_error:

                    if attempt < 2:
                        time.sleep(
                            2 ** (attempt + 1)
                        )
                        continue

                    break

                break

    return (
        "⚠️ Gemini is temporarily unavailable right now.\n\n"
        "I tried the available Gemini models, but the AI service "
        "did not accept the request.\n\n"
        "Please wait a few seconds and try again."
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        careers=CAREERS
    )


# ============================================================
# CHAT PAGE
# ============================================================

@app.route("/chat")
@login_required
def chat():

    return render_template(
        "chat.html"
    )


# ============================================================
# CAREERS PAGE
# ============================================================

@app.route("/careers")
def careers():

    return render_template(
        "careers.html",
        careers=CAREERS
    )


# ============================================================
# ROADMAPS PAGE
# ============================================================

@app.route("/roadmaps")
def roadmaps():

    return render_template(
        "roadmaps.html",
        roadmaps=ROADMAPS
    )


# ============================================================
# ABOUT PAGE
# ============================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Please enter email and password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        if user is None:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # PASSWORD CHECK
        # ----------------------------------------------------

        stored_password = None

        # New database
        if "password" in user.keys():
            stored_password = user["password"]

        # Old database compatibility
        elif "password_hash" in user.keys():
            stored_password = user["password_hash"]

        if not stored_password:

            flash(
                "Account password data is missing. "
                "Please register again.",
                "error"
            )

            return render_template(
                "login.html"
            )

        if not check_password_hash(
            stored_password,
            password
        ):

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # LOGIN SUCCESS
        # ----------------------------------------------------

        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        return redirect(
            url_for("chat")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please fill all fields.",
                "error"
            )

            return render_template(
                "register.html"
            )

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return render_template(
                "register.html"
            )

        password_hash = generate_password_hash(
            password
        )

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (name, email, password, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    password_hash,
                    datetime.now().isoformat()
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "An account with this email already exists.",
                "error"
            )

            return render_template(
                "register.html"
            )

        conn.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# API - ALL CAREERS
# ============================================================

@app.route("/api/careers")
def api_careers():

    return jsonify(
        CAREERS
    )


# ============================================================
# API - CAREER RECOMMENDATION
# ============================================================

@app.route(
    "/api/recommend",
    methods=["POST"]
)
def recommend():

    data = request.get_json(
        silent=True
    ) or {}

    answers = data.get(
        "answers",
        data
    )

    if isinstance(answers, str):

        query = answers.lower()

    else:

        query = " ".join(
            str(value)
            for value in answers.values()
        ).lower()

    results = []

    for career in CAREERS:

        score = 0

        searchable_text = " ".join([
            career["title"],
            career["description"],
            career["overview"],
            career["what_you_do"],
            career["suitable_for"],
            career["future_scope"],
            " ".join(career["skills"])
        ]).lower()

        words = query.split()

        for word in words:

            if len(word) < 3:
                continue

            if word in searchable_text:
                score += 1

            for skill in career["skills"]:

                if word in skill.lower():
                    score += 3

        results.append({
            "career": career,
            "score": score
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    top_results = [
        item["career"]
        for item in results[:5]
    ]

    return jsonify({
        "recommendations": top_results
    })


# ============================================================
# API - CHAT
# ============================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
@login_required
def api_chat():

    data = request.get_json(
        silent=True
    ) or {}

    message = str(
        data.get(
            "message",
            ""
        )
    ).strip()

    if not message:

        return jsonify({
            "error": "Please enter a message."
        }), 400

    user_id = session["user_id"]

    conn = get_db()

    previous_rows = conn.execute(
        """
        SELECT role, message
        FROM chats
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (user_id,)
    ).fetchall()

    history = [
        {
            "role": row["role"],
            "message": row["message"]
        }
        for row in reversed(previous_rows)
    ]

    # Save user message
    conn.execute(
        """
        INSERT INTO chats
        (user_id, role, message, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            "user",
            message,
            datetime.now().isoformat()
        )
    )

    conn.commit()

    # Generate AI response
    reply = ai_reply(
        message,
        history
    )

    # Save assistant response
    conn.execute(
        """
        INSERT INTO chats
        (user_id, role, message, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            "assistant",
            reply,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "reply": reply
    })


# ============================================================
# API - CHAT HISTORY
# ============================================================

@app.route("/api/history")
@login_required
def api_history():

    user_id = session["user_id"]

    conn = get_db()

    rows = conn.execute(
        """
        SELECT role, message, created_at
        FROM chats
        WHERE user_id = ?
        ORDER BY id ASC
        LIMIT 100
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    history = [
        {
            "role": row["role"],
            "message": row["message"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]

    return jsonify(
        history
    )


# ============================================================
# API - CLEAR CHAT
# ============================================================

@app.route(
    "/api/clear-chat",
    methods=["POST"]
)
@login_required
def clear_chat_api():

    user_id = session["user_id"]

    conn = get_db()

    conn.execute(
        """
        DELETE FROM chats
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return (
        "Internal server error. "
        "Please check the Flask terminal.",
        500
    )


# ============================================================
# START FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )