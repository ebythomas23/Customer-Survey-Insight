import ast
import json
from typing import Dict, Any, List

import pandas as pd
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import SystemMessage, UserMessage, ModelInfo
from dotenv import load_dotenv

from config.constants import MODEL_OPENAI

load_dotenv()


async def ClusterLabelling(
    input_csv_path: str = "data/df_with_clusters.csv",
    output_csv_path: str = "data/output.csv",
    topics_column: str = "all_topics_discussed",
    cluster_ids_column: str = "topic_cluster_ids",
) -> Dict[str, Any]:
    """
    Step 3: Cluster Labelling / Theme Definition (simple, straightforward implementation)

    - Reads the clustered CSV from Step 2 containing per-row topics and parallel cluster IDs.
    - Builds cluster -> topics mapping and uses an LLM to assign a short business-friendly label per cluster.
    - Explodes to one row per topic with columns: `topic_discussed` and `general_topic_l1` (cluster label).
    - Writes the enriched, labeled CSV to `output_csv_path`.
    """
    df = pd.read_csv(input_csv_path)

    topics_series = df[topics_column].apply(ast.literal_eval)
    cluster_ids_series = df[cluster_ids_column].apply(ast.literal_eval)

    clusters: Dict[int, List[str]] = {}
    for topics, ids in zip(topics_series, cluster_ids_series):
        for t, cid in zip(topics, ids):
            clusters.setdefault(int(cid), []).append(str(t))

    client = OpenAIChatCompletionClient(
        model=MODEL_OPENAI,
        model_info=ModelInfo(vision=False, function_calling=True, json_output=True, structured_output=True, family="openai"),
    )

    cluster_labels: Dict[int, str] = {}
    for cid, tlist in clusters.items():
        prompt = (
            "You assign a single short, business-friendly theme label for a cluster of insurance survey topics.\n"
            "You will be given a semicolon-separated sample of topic phrases from the `all_topics_discussed` column that all belong to the SAME cluster.\n"
            "Requirements:\n"
            "- 2–5 words, noun phrase, business-friendly.\n"
            "- Generalize across the listed topics (no quotes, no IDs, no counts).\n"
            "- Avoid product/channel names and sentiment words unless central to the theme.\n"
            "- Capture the shared theme succinctly; avoid repeating the example phrases verbatim.\n"
            "Return STRICT JSON only (no markdown fences, no extra text): {\"label\": \"<Label>\"}.\n\n"
            "Example 1:\n"
            "Topics in cluster (from all_topics_discussed): Confusing claims process; Unclear claim steps; Too many claim forms\n"
            "Output: {\"label\": \"Claims process complexity\"}\n\n"
            "Example 2:\n"
            "Topics in cluster (from all_topics_discussed): Long claim processing time; Slow payouts\n"
            "Output: {\"label\": \"Claims turnaround delays\"}"
        )
        sample = "; ".join(list(dict.fromkeys(tlist))[:12])
        messages = [
            SystemMessage(content=prompt),
            UserMessage(content=f"Topics in cluster (from all_topics_discussed): {sample}", source="user"),
        ]
        result = await client.create(messages)
        content = result.content if isinstance(result.content, str) else "{}"
        label = json.loads(content)["label"]
        cluster_labels[int(cid)] = label

    await client.close()

    rows = []
    for _, row in df.iterrows():
        topics = ast.literal_eval(row[topics_column])
        ids = ast.literal_eval(row[cluster_ids_column])
        for t, cid in zip(topics, ids):
            r = row.to_dict()
            r["topic_discussed"] = t
            r["general_topic_l1"] = cluster_labels[int(cid)]
            rows.append(r)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(output_csv_path, index=False)

    return {
        "status": "success",
        "clusters": len(cluster_labels),
        "output_path": output_csv_path,
        "total_rows": len(out_df),
        "model": MODEL_OPENAI,
    }
