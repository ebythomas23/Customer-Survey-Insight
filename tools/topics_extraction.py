import json
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage, SystemMessage, ModelInfo

from config.constants import MODEL_OPENAI

load_dotenv()


async def TopicExtraction(
    input_csv_path: str = "data/input.csv",
    output_csv_path: str = "data/df_with_topics.csv",
    text_column: str = "call_transcrpt",
) -> Dict[str, Any]:
    """
    Reads the survey CSV, calls an LLM per row to extract topics, and writes an intermediate CSV
    with new columns for topics, supporting quote, reasoning, and sentiment.

    """
    df = pd.read_csv(input_csv_path)
    
    prompt = (
        "You extract a list of key topics or issues mentioned in each insurance customer survey comment. "
        "Each topic should be concise yet descriptive, allowing a business user to understand what action might be needed. "
        "A single survey response may contain multiple topics. "
        "Return strict JSON only with keys: topics (array of 2-5 short phrases, 2-6 words each), "
        "supporting_quote (<=160 chars, verbatim from text), reason (1-2 sentences), "
        "sentiment (Negative|Neutral|Positive).\n"
        "Example: \n"
        "Survey: The claims process is confusing and slow. I waited weeks for resolution.\n"
        "Topics: ['Confusing claims process', 'Long claim turnaround time']"
    )

    topics_list: List[List[str]] = []
    quotes: List[str] = []
    reasons: List[str] = []
    sentiments: List[str] = []
    process_times: List[str] = []
    model_versions: List[str] = []

    client = OpenAIChatCompletionClient(
        model=MODEL_OPENAI,
        model_info=ModelInfo(vision=False, function_calling=True, json_output=True, structured_output=True, family="openai"),
    )
    try:
        for _, row in df.iterrows():
            raw_text = str(row.get(text_column, ""))

            messages = [
                SystemMessage(content=prompt),
                UserMessage(content=f"Extract topics in strict JSON.\nText: {raw_text}", source="user"),
            ]

            result = await client.create(messages)
            content = result.content if isinstance(result.content, str) else "{}"
            
            # Strip markdown code fences if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
           
            topics = [str(t).strip() for t in data.get("topics", []) if str(t).strip()]
            topics = list(dict.fromkeys(topics))[:5]

            topics_list.append(topics)
            quotes.append((data.get("supporting_quote") or "")[:160])
            reasons.append(data.get("reason") or "")
            sentiments.append(data.get("sentiment") or "Neutral")
            process_times.append(datetime.now().isoformat(timespec="seconds"))
            model_versions.append(MODEL_OPENAI)
    finally:
        await client.close()

    # Add columns
    df["all_topics_discussed"] = topics_list
    df["supporting_quote"] = quotes
    df["ai_topic_reasoning"] = reasons
    df["customer_sentiment"] = sentiments
    df["process_time"] = process_times
    df["model_version"] = model_versions

    df.to_csv(output_csv_path, index=False)

    return {
        "status": "success",
        "rows": int(len(df)),
        "output_path": output_csv_path,
        "model": MODEL_OPENAI,
    }

