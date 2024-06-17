# Add this to chain class to access it as a tool from agent.

```python
@tool(ClinicalSummaryChain().name, args_schema=ClinicalSummaryChain().input_type)
def get_tool(**kwargs):
    """
    Summarize the clinical document to a given word count.
    The input is a dict with the following keys:
        clinical_document (str): The clinical document to summarize.
        word_count (str): The number of words to summarize to.
    """
    return ClinicalSummaryChain().chain.invoke(kwargs)
```