# Neuro Symbolic Approach Feature

The Neuro Symbolic Approach enhances the original Rule-Agent project by combining natural language processing with symbolic reasoning via an ontology and machine-learning components. This README provides detailed instructions on how to set up and use this new feature.

---

## Overview

The Neuro Symbolic feature integrates several new capabilities:
- **Ontology Management:**  
  An OWL ontology (defined in `ontology_engine.py`) that describes engine-related classes (e.g., `Engine`, `OilEngine`, `ElectricEngine`), components (e.g., `Piston`, `Battery`), and relationships (e.g., `CausesFailure`).

- **Machine Learning Integration:**  
  Training data is generated from the ontology and used to train a logistic regression model (in `ml_model.py`) to convert natural language input into a structured logical form.

- **Evaluation and Feedback:**  
  Logical forms generated from user inputs are validated against the ontology using evaluation functions (in `evaluation.py`). Detailed feedback and explanations are provided for each logical evaluation.

- **Enhanced Prompt Handling:**  
  New prompt templates (defined in `prompt_handler.py` and `prompts.py`) integrate ontology information and evaluation results into the LLM’s responses.

---

## Directory Structure

The Neuro Symbolic components are contained in the `rule-agent/neuro_symbolic/` directory. Key files include:

```
rule-agent/
├── neuro_symbolic/
│    ├── ontology_engine.py    # Defines and sets up the ontology
│    ├── ml_model.py           # Generates training data & trains the ML model
│    ├── evaluation.py         # Evaluates logical forms against the ontology
│    └── prompt_handler.py     # Assembles context-rich prompts for LLM integration
```

Additional configuration and utility files (e.g., `config.py`, `Utils.py`) support these features.

---

## Setup Instructions

### 1. Install Dependencies

Ensure you have Python 3.x installed. Install the required packages by running:

```bash
pip install -r requirements.txt
```

The dependencies include additional packages for the Neuro Symbolic feature, such as:
- `owlready2` (for ontology management)
- `scikit-learn` (for ML model training)
- `langchain_ibm` and `pydantic` (for integration with the LLM and data validation)

### 2. Prepare the Ontology File

The ontology is created and maintained by the `ontology_engine.py` module:
- **Default Behavior:**  
  When first run, the ontology is created dynamically and saved as `engine_ontology.owl` (in the project root by default).
- **Custom Ontology:**  
  If you have your own OWL ontology file, place it in the project root or update the `ONTOLOGY_FILE` constant in `ontology_engine.py` to point to your file.
- **Ontology Contents:**  
  The ontology defines engine classes (e.g., `Engine`, `OilEngine`), components (e.g., `Piston`, `OilPump`, `Battery`, `Motor`), and a relationship (`CausesFailure`) used for evaluating logical forms.

### 3. Set Environment Variables

Create or update your `.env` file (or set environment variables directly) with the following keys:

```env
USE_NEURO_SYMBOLIC=1
WATSONX_API_KEY=your_watsonx_api_key
PROJECT_ID=your_project_id
WATSONX_URL=https://api.watsonx.example.com
LOG_LEVEL=DEBUG
DATADIR=./data
```

- **USE_NEURO_SYMBOLIC:**  
  Set to `1` to enable the advanced Neuro Symbolic pipeline; otherwise, the system will default to the original NL → JSON processing.

### 4. Configure the Project

Review `config.py` for configuration parameters such as decoding settings (e.g., `max_new_tokens`, `temperature`) and API credentials required for WatsonxLLM.

---

## Usage Instructions

### Starting the Application

1. **Run the Main Application:**

   Launch your main application (which utilizes `RuleAIAgent.py`). The agent will inspect the `USE_NEURO_SYMBOLIC` environment variable:
   - **Advanced Mode Enabled:**  
     - Loads and, if needed, creates the ontology.
     - Generates training data and trains the ML model.
     - Converts natural language queries into logical forms.
     - Validates logical forms against the ontology and produces human-readable evaluation feedback.
     - Combines neural and symbolic reasoning to produce responses.
   - **Advanced Mode Disabled:**  
     - Falls back to the original NL → JSON pipeline.

2. **Example:**

   ```bash
   python main.py
   ```

   (Replace `main.py` with the entry point of your application.)

### Testing the Neuro Symbolic Pipeline

- **Evaluation Module Test:**

  You can test logical form evaluations by running:

  ```bash
  python -m rule-agent.neuro_symbolic.evaluation
  ```

  This script (with a testing block) will load the ontology, evaluate sample logical statements, and print detailed feedback.

### Customizing the Ontology

- **Edit the Ontology:**

  To modify the engine domain ontology:
  - Open `rule-agent/neuro_symbolic/ontology_engine.py`.
  - Add, modify, or remove classes, properties, and instances as needed.
  - After making changes, delete or update the `engine_ontology.owl` file to allow the changes to take effect.

- **Reloading the Ontology:**

  The system uses the `sync_reasoner()` function from Owlready2 to update and infer new relationships. Ensure the ontology is correctly saved and synchronized.

---

## Debugging and Logging

- The system uses a logging framework configured in `Utils.py`. To view detailed logs, set `LOG_LEVEL=DEBUG` in your environment.
- Check console output for messages regarding ontology creation, ML model training, and evaluation feedback.

---

## Troubleshooting

- **Ontology Not Found:**  
  Ensure the `engine_ontology.owl` file is in the expected location or update its path in `ontology_engine.py`.

- **ML Model Issues:**  
  Verify that training data is being generated from your ontology. Check logs for details during the model training phase in `ml_model.py`.

- **Advanced Mode Not Activating:**  
  Confirm the environment variable `USE_NEURO_SYMBOLIC` is set to `1`.

---

## Conclusion

The Neuro Symbolic Approach provides a powerful enhancement to the Rule-Agent project by merging deep neural models and symbolic reasoning. By following the steps above, you can set up and leverage this advanced capability to generate more interpretable and validated outputs.

For further assistance, refer to the project documentation or contact the development team or contact [me](https://github.com/ruslanmv/).
