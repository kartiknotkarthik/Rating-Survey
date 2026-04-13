# Phase 2: LLM Analysis Engine (Groq Integration)

This folder contains the implementation of Phase 2: **LLM Analysis & Insight Generation**.

## Features
- **Groq Integration**: Uses Llama-3-70b for high-speed, high-quality analytical reasoning.
- **Theme extraction**: Automatically identifies 3-5 recurring themes from raw review text.
- **Pulse Synthesis**: Generates a one-page strategic report containing:
    - **Top 3 Themes**: Detailed analysis of user sentiment.
    - **3 User Quotes**: impactful, PII-free testimonials.
    - **3 Action Ideas**: Practical roadmap recommendations.
- **Automated Data Discovery**: Automatically picks up the latest JSON dataset from the `/data` folder.

## Prerequisites
1. Ensure your **GROQ_API_KEY** is set in the `.env` file at the project root.
2. Ensure Phase 1 has been run and data is available in `../data/`.

## Usage
Run the analysis script:
```bash
python analyze_data.py
```

## Output
The generated pulse note is saved in the `reports/` subdirectory as Markdown.
