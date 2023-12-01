import os

from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


class GPT:
    def __init__(self, query, model="gpt-3.5-turbo"):
        self.query = query
        self.model = model

    def get_response(self):
        pass


class MilestoneGPT(GPT):
    def __init__(self, query, model="gpt-4"):
        super().__init__(query, model)

    def get_response(self):
        messages = [
            {
                "role": "system",
                "content": f"사용자는 너에게 어떤 프로젝트의 설명과 해당 프로젝트에 생성되어 있는 마일스톤의 정보를 json 형식으로 줄 것이다.\n"
                f"생성되어 있는 마일스톤은 있을 수도 있고 없을 수도 있다.\n\n"
                f"사용자의 입력 형식: \n"
                "{ \n"
                f'"project_description": string, '
                '"milestones": [{"title": string, "tags": list[string]}] or [] \n'
                "}\n\n"
                '"project_description"는 markdown 문법을 준수하는 문자열이다. \n'
                '"milestones"는 존재하는 마일스톤의 정보를 담고 있는 리스트이다. \n\n'
                f"사용자의 입력 형식을 보고 현 상황에서 (가장 먼저 OR 다음으로) 진행해야 하는 마일스톤 하나의 제목과 태그(최대 10개)를 생성하면 된다. 다음은 마일스톤에 대한 설명이다.\n"
                f"마일스톤은 프로젝트를 완성하기 위한 일련의 과정으로 여러개의 마일스톤이 모여서 하나의 프로젝트를 완성한다.\n"
                f"title은 무조건 한글로 대답해야 한다. tag는 기술 용어의 경우 일반적으로 영어로 사용되는 경우만 허용한다.\n"
                f"다음은 출력할 형식이다. 이 json 형식을 따라야 하고 따를 수 없는 경우(입력 형식 INVALID 또는 정해진 형식을 따를 수 없는 상황)에는"
                f"'CANT_UNDERSTAND' 문자열을 출력한다.\n"
                "'response': {'title': 'string', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5' \
                , 'tag6', 'tag7', 'tag8', 'tag9', 'tag10']}\n\n"
                f"즉, 'CANT_UNDERSTAND' 문자열이나 위에 정의된 출력 형식을 준수하여야 한다. 이외는 허용하지 않는다.",
            },
            {"role": "user", "content": self.query},
        ]

        response = client.chat.completions.create(model=self.model, messages=messages)
        answer = response.choices[0].message.content
        return answer


if __name__ == "__main__":
    gpt = MilestoneGPT(
        '{"project_description": # Prompt Day Project \n ## 주제 \n\n \
                        - SKT 프롬프트 데이 공모전 준비를 위한 프로젝트 진행방입니다. \n \
                        - 저희는 "타로몽" 이라는 것을 주제로 프로젝트를 진행할 예정입니다. \n \
                        ## 진행방식 \n\n \
                        - 기본적으로 애자일 스크럼 방식으로 진행 \n \
                        - 1주 단위로 스프린트 진행 \n \
                        - 1일 단위로 스크럼 진행 \n\n \
                        ### 1주차 \n \
                        - 기획 및 디자인 구체화 \n\n \
                        ### 2주차 \n \
                        - FE, BE 구현 \n\n \
                        ### 3주차 \n \
                        - 시연영상 촬영 \n\n \
                        ## 팀 구성 \n \
                        - FE 2명 \n \
                        - BE 2명}, {"milestones": []}'
    )
    print(gpt.get_response())
