# PragyanAI_Product_PCB_Design_Verification_Solution
pcb-review-copilot/
├── .github/
│   └── workflows/            # CI/CD pipelines (Testing, LVM deployment)
├── assets/                   # Static assets (logos, hardware diagrams)
├── components/               # Streamlit UI Components
│   ├── analysis.py           # Defect panel & Rework UI
│   ├── sidebar.py            # Navigation & Settings
│   ├── uploader.py           # Multi-format file ingestion
│   └── workspace.py          # PCB Digital Twin & Heatmaps
├── data/
│   ├── benchmarks/           # Standard PCB defect datasets (Open Source)
│   └── ipc_standards/        # Vector store for RAG (IPC-2221, IPC-6012)
├── logic/                    # Core Intelligence Layer
│   ├── agents/               # Specialized Agent definitions
│   │   ├── compliance_agent.py # RAG-based IPC checks
│   │   ├── physics_agent.py    # Thermal/EMI simulation logic
│   │   └── vision_agent.py     # LVM (LLaVA/Moondream) integration
│   ├── agent_orch.py         # LangGraph state machine & orchestration
│   ├── llm_config.py         # GROQ LPU & Model parameters
│   └── physics_rules.py      # Hard-coded engineering constraints
├── notebook/                 # R&D for Vision Transformer (ViT) training
├── tests/                    # Unit tests for agents & physics engine
├── app.py                    # Main Entry Point (Streamlit)
├── styles.py                 # Enterprise Theme (CSS)
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
