from agents.SurveyInsightAgent import getSurveyInsightAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat


async def get_survey_insight_team():
    agent=  await getSurveyInsightAgent()

    team = RoundRobinGroupChat(
            participants=[agent],
            max_turns=2,
            termination_condition=TextMentionTermination('STOP')
        )
    return team
