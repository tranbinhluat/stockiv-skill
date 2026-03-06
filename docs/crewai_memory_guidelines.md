# CrewAI Memory Guidelines

This document outlines the best practices for managing, clearing, and fine-tuning the long-term memory systems inherent to CrewAI.

## Memory Systems in CrewAI
When `memory=True` is enabled in a Crew, it utilizes three internal data stores:
1. **Short-Term Memory / Entity Memory:** Backed by ChromaDB (locally) and embeddings logic to recall recent task context and entity relationships.
2. **Long-Term Memory:** Backed by SQLite. Accumulates global insights across many sessions.

## 1. Resetting or Clearing Memory
Over time, continuous evaluation of stocks can pollute the memory system with outdated predictions. To clear memory globally for your agents, do not attempt to delete the SQLite or ChromaDB files manually, as this can corrupt the state.

**Best Practice (CLI Reset):**
Use the built-in CrewAI CLI to flush the memory.
```bash
# Reset all memories (long-term, short-term, entity)
crewai reset-memories --all

# Reset specifically for one agent (Requires Agent Role Name)
crewai reset-memories --long-term --agent "Sentiment Analyst"
```

## 2. Fine-Tuning CrewAI Memory (RAG Hyperparameters)
"Fine-tuning" in the context of CrewAI's memory system refers to adjusting the Retrieval-Augmented Generation (RAG) hyperparameters, rather than retraining a neural network.

You can tune how the Agent recalls older memories by passing specific configurations to the Memory system.

### Recency Weighting
If your Sentiment Analyst is clinging too strongly to old market conditions, you can configure the memory storage to prioritize recent inputs more heavily:

```python
from crewai import Crew
from crewai.memory import ShortTermMemory, LongTermMemory

crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True, # Enable global memory
    # Tuning configurations could be applied via custom memory class injections
    # according to the latest CrewAI RAG documentation.
)
```
*Note: CrewAI continues to evolve its memory API to expose attributes like `recency_weight` and `recency_half_life_days`. By tuning these, you instruct the embedder to rank newer documents higher during cosine similarity searches.*

## 3. Base Model Fine-Tuning vs Memory Tuning
It is critical to distinguish between tuning the **Database** (memory vectors) and tuning the **Brain** (the LLM).

- **Memory Tuning (ChromaDB):** Adjusts *what* facts the agent recalls from previous runs. This is fast, programmatic, and controlled via configurations and the `crewai reset-memories` CLI.
- **Model Fine-Tuning (LLM):** If the Agent fundamentally fails to understand financial jargon or outputs in the wrong tone repeatedly (despite prompt engineering), you would use external tools (like LoRA/QLoRA on HuggingFace) to fine-tune a model weight file. You would then load that specific fine-tuned model via Ollama or vLLM, and point CrewAI to use it via the standard `LLM` class.
