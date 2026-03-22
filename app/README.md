# CISI Revision Hub

Streamlit-based study interface for CISI Level 6 Regulation & Compliance.

## Setup

1. Copy this folder into your CISI project root (alongside the `knowledge-base/` directory)
2. Install dependencies: `pip install -r requirements.txt`
3. Double-click **`launch.bat`** — opens in your browser at `localhost:8501`

## Structure Expected

```
your-project/
├── knowledge-base/
│   ├── topics/
│   │   ├── part-1-regulatory-framework/
│   │   ├── part-2-fca-handbook/
│   │   ├── ...
│   │   └── risk-in-financial-services/
│   ├── question-bank/
│   │   ├── section-a/
│   │   ├── section-b/
│   │   └── section-c/
│   └── reference/
├── app.py          ← this file
├── launch.bat
└── requirements.txt
```

## Features

- **Sidebar navigation** — browse by Part, Question Bank section, or Reference
- **Full-text search** — find any keyword across all notes
- **Session progress** — ✅ marks topics you've read this session
- **Stats dashboard** — landing page shows total/viewed/remaining counts
- **Clean reading view** — optimised typography for study content
