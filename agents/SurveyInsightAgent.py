from autogen_agentchat.agents import AssistantAgent

from models.openai_model_client import get_model_client
from dotenv import load_dotenv

from prompts.system_prompt import SurveyInsightAgent_message

from tools.topics_extraction import TopicExtraction
from tools.topic_clustering import  TopicClustering
from tools.cluster_labelling import ClusterLabelling


async def getSurveyInsightAgent():
    model_client= get_model_client()

    survey_insight_agent = AssistantAgent(
        name ='SurveyInsightAgent',
        model_client= model_client,
        description = " an agent that is to run a 4-step, end-to-end pipeline that converts raw customer survey CSV data into an enriched, analytics-ready CSV and a concise set of decision-ready insights for senior leadership ",
        system_message= SurveyInsightAgent_message,
        tools=[TopicExtraction,TopicClustering,ClusterLabelling],
        reflect_on_tool_use=True
        )
    return survey_insight_agent


