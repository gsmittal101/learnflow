

import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners  import InMemoryRunner
from google.genai import types

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "project-70e0c028-d88a-45d9-839"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"


#Creare an agent with a specific model and instructions
tutor = Agent(
    name="adk_tutor",
    model="gemini-3.7-flash",
    description="Explain Google ADK concept to student",
    instruction=("you are a patient tutor for a class learning the Google agent" 
                  "development kit answer in at most five short sentences"
                  "use plain words prefer a concrete example over an abstract definition."
                  "If a question is not about agents or adk say no in one sentence."
                  )
)

APP_NAME = "my_adk_app_1"
USER_ID = "Gaurav"

async def main() -> None:
    #Run the agent
    runner = InMemoryRunner(
        agent=tutor,
        app_name=APP_NAME
    )

    #Seesion of the agent
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    question1 = "What is difference between a Google agent and Runner in Google ADK?"
    #Prepare the mesasge to send to the agent
    message = types.Content(
    role = "user",
    parts = [types.Part(
            text=question1)]

    )

    #Send the message to the agent and get the response

    response = ""
    for event in runner.run(
    user_id=USER_ID,
    session_id=session.id,
    new_message=message

    ):

        if event.content:
            for part in event.content.parts:
                if part.text:
                    response += part.text
      
    print(response) 

    # async for eventin runner.run.asy(
    #     user_id=USER_ID,
    #     session_id=session.id,
    #     new_message=message
    # ):

    #     if event.content:
    #         print(event.content[0].text)
    #     elif event.error:
    #         print(event.error.message)


if __name__ == "__main__":
    asyncio.run(main())
    