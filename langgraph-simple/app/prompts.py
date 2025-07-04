from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage
from .state import AgentState


class Prompts:
    @staticmethod
    def gen_prompt(
        system_prompt: str, user_prompt: str, state: AgentState
    ) -> list[AnyMessage]:
        user_prompt = user_prompt.format(**state)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        return messages

    @classmethod
    def router(cls, state: AgentState) -> list[AnyMessage]:
        ROUTER_SYSTEM = """
        You are HR expert. Your job on this step is to determine the role the user is applying for.
        Focus on a specific role like engineer, data scientist, recruiter, accountant, etc. 
        If the role is not directly specified, you can determine the role based on the user's profile and interests when provided.
        """
        ROUTER_PROMPT = """
        <user_query>
        {query} 
        </user_query>
        <instructions>
        - You will extract only the role from the user query. Do not include any other information.
        - Output the role in a structured format under the `role` key.
        - If the user query is not clear about the role or the user's interests and profile is not provided,
        output None
        </instructions>
        <examples>
        - "I am a data scientist looking for jobs at company X" -> {{"role": "data scientist"}}
        - "What open positions are available at company X for a software engineer?" -> {{"role": "software engineer"}}
        - "What are the open jobs for factored ai?" -> {{"role": "None"}}
        - "I'm interested in bulding Machine Learning models, what options are availabel for me?" -> {{"role": "machine learning engineer"}}
        </examples>
        
        """
        return cls.gen_prompt(ROUTER_SYSTEM, ROUTER_PROMPT, state)

    @classmethod
    def agent(cls, state: AgentState) -> list[AnyMessage]:
        AGENT_SYSTEM = """
        You are HR expert. Your job on this step is to provide the user with the best job postings for the role and company they are applying for.
        If there are no job postings for the role, you should say so. Do no make up any job postings, only use the ones provided.
        """
        AGENT_PROMPT = """
        <user_query>
        {query} 
        </user_query>
        <role>
        {role}
        </role>
        <instructions>
        - You will search the web for the company's job postings.
        - You will select the one web search result that has the most relevant information for job postings options.
        - If this job posting has links, you will scrape the links to get the job postings.
        - Based on the job postings, you will provide the user with the best job postings for the role and company they are applying for.
        - Please provide the user with a short sentence with a summary of the job posting, requirements, and responsibilities. 
        - If more than one job posting is found, you will provide the user with a list of the job postings. Max 3 job postings.
        - Always include the link of the specific job posting on the summary. If not found, provide the link of the general job postings page.
        </instructions>
        Use the following messages and tool calls to determine the next step.
        <messages>
        {messages}
        </messages>
        
        """
        return cls.gen_prompt(AGENT_SYSTEM, AGENT_PROMPT, state)
