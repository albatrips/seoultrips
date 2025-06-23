from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
import base64

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pathlib import Path


router = APIRouter()
# templates = Jinja2Templates(directory="server/templates")

@router.post("/image_upload")
def image_upload_for_check_quest(quest:str, image_base64:str):
    """
        Image Data를 받아서 base64로 변환한 뒤, 퀘스트 평가를 진행한다.
    """

    image_data = f"data:image/png;base64,{image_base64}"

    system_message = SystemMessage(
        content=[
            """
            목표 : 인증샷을 비교하여 미션을 수행하였는지에 대한 판단 여부를 반환한다.
            출력 결과 :
            {
                "score" : "",
                "feedback" : ""
            }
            """
        ]
    )


    vision_message = HumanMessage(
        content=[
            {"type": "text", "text": f"미션: {quest}"},
            {
                "type" : "image_url",
                "image_url":{
                    "url" : image_data,
                    "detail":"auto"
                }
            }
        ]
    )

    # TODO : Model 바꾸기 // factory
    vision_model = ChatOpenAI(model_name="gpt-4o-mini")

    output = vision_model.invoke([system_message, vision_message])


    # TODO : Return page , DATA 수정
    return templates.TemplateResponse(".html", {
        "request": "hi"
    })

def get_base64_image():
    """
        base64_image가 아닌 이미지를 받았을 경우 처리할 곳.
        로컬에서 테스트 할 때는 root 경로에 /local/images/폴더 만들어서 테스트를 진행했었음.
        임시 저장 경로 정해지면 거기에 맞춰서 변경 작업 진행
    :return:
    """
    path_root = Path(__file__).resolve().parent.parent.parent.resolve()
    base_image_path = path_root / "local" / "images"
    base_image_path = str(base_image_path).replace("\\", "/")

    with open(base_image_path  + "/test.png", "rb") as f:
        binary_data = f.read()
        image_base64 = base64.b64encode(binary_data).decode("utf-8")

    return image_base64