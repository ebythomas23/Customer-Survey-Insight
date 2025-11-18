import ast
from typing import Dict, Any, List

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os 
load_dotenv()


async def TopicClustering(
    input_csv_path: str = "data/df_with_topics.csv",
    output_csv_path: str = "data/df_with_clusters.csv",
    topics_column: str = "all_topics_discussed",
    num_clusters: int = 12,
) -> Dict[str, Any]:
    """
    Step 2 tool: Cluster topic phrases across all rows using OpenAI embeddings + KMeans.

    - Reads the enriched CSV from Step 1 (with a list column of topic phrases).
    - Clusters unique topic phrases into `num_clusters` groups using semantic embeddings.
    - Adds a new column `topic_cluster_ids` with the cluster id for each topic in the row.
    - Writes ONLY the updated dataframe to `output_csv_path`.
    """
    df = pd.read_csv(input_csv_path)

    topics_series = df[topics_column].apply(ast.literal_eval)
    unique_topics: List[str] = sorted({t for lst in topics_series for t in lst})

    client = AsyncOpenAI( api_key= os.getenv('OPENAI_EMBEDDING_API_KEY'))
    response = await client.embeddings.create(
        input=unique_topics,
        model="text-embedding-3-small",
    )
    embeddings = np.array([item.embedding for item in response.data])
    await client.close()

    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    topic_to_cluster = {topic: int(label) for topic, label in zip(unique_topics, labels)}

    df["topic_cluster_ids"] = topics_series.apply(lambda lst: [topic_to_cluster[t] for t in lst])

    df.to_csv(output_csv_path, index=False)

    return {
        "status": "success",
        "clusters": int(num_clusters),
        "output_path": output_csv_path,
        "embedding_model": "text-embedding-3-small",
        "unique_topics": int(len(unique_topics)),
    }
