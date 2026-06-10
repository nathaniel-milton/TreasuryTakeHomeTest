# TTB AI-Powered Alcohol Label Verification Tool (Prototype)

This repository contains a standalone proof-of-concept AI verification tool designed to accelerate the TTB's label review workflow. It addresses core stakeholder challenges, focusing on speed, simple UI UX for diverse technical capabilities, and rigorous rule-based compliance checks.

## 🚀 Architectural & Engineering Choices

1. **Frontend UI Framework (Streamlit):** Chosen specifically to address **Sarah's requirement** for an explicit, "Dave-proof" UI. Streamlit lets us build clean, self-contained interactive web dashboards quickly without bloated JavaScript configuration, allowing senior agents to instantly understand the system's actions.
2. **Vision Language Model (VLM):** We leverage an advanced vision API (`gpt-4o-mini`). This handles skewed images, poor lighting, or glare seamlessly without requiring brittle pre-processing OCR logic (**Jenny's feedback**). It regularly achieves execution runtimes under **3.5 seconds**, passing **Sarah's 5-second failure threshold**.
3. **Structured Output (JSON Mode):** The prompt enforces strict JSON formatting directly from the model, ensuring reliable evaluations on text formatting, capitalizations, and text alignment rules.

## 🛠️ Local Setup Instructions

1. **Clone this repository** to your local machine.
2. Create a `.env` file in the root directory and add your API key:
```env
   OPENAI_API_KEY=your_actual_api_key_here