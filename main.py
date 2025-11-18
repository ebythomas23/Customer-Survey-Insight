import asyncio
from teams.survey_insight import get_survey_insight_team
from autogen_agentchat.ui import Console

async def main():
    team = await get_survey_insight_team()

    try: 
        #task ="perform the step1"
        #  async  for message in team.run_stream(task= task):
        #      print(message)
        await Console(team.run_stream(task="perform analysis"))

    except Exception as e:
        print(e)


if __name__ == "__main__":
     asyncio.run(main())
