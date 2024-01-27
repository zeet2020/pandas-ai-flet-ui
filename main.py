import flet as ft
import pandas as pd

from pandasai import SmartDataframe
from pandasai import Agent
from pandasai.llm.openai import OpenAI
#from pandasai.skills import skill


#add the openai token here
llm = OpenAI(api_token="",temperature=0)




helpLine = """
Excel is loaded, agent is ready to answer your questions
helpful command to interact with agent use below token for questions and clarification
`#question` your question
`#clarify:` your question
`#explain:` 
`#rephrasing:` your question
"""
class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

class ChatMessage(ft.Row):

    def __init__(self, message: Message,pageRef):
        super().__init__()

        self.vertical_alignment="start"
        #print(self.width)
        self.controls=[
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(message.user_name)),
                    color=ft.colors.WHITE,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),

                ft.Column(
                    [
                        ft.Text(message.user_name, weight="bold"),

                        ft.Text(message.text, selectable=True, width=(pageRef.width-10))
                    ],
                    tight=True,
                    spacing=5,
                ),
            ]

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

def main(page: ft.Page):
    _agent:Agent

    page.horizontal_alignment = "stretch"
    page.title = "Pandas Ai"


    def join_chat():
            page.pubsub.send_all(
                Message("Agent",message_type="chat_message",text=helpLine)
            )


    def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all(Message("You", new_message.value, message_type="chat_message"))
            new_message.value = ""
            new_message.focus()
            page.update()

    def to_agent(message):
        if len(message.text) > 0:
            #print(message.text)
            mesg = message.text
            res = "Unknow query"
            _agent = page.session.get("agent")
            if len(mesg) != len(mesg.replace("#question","")):
                #print(mesg.replace("#question","").strip())
                res = _agent.chat(query=mesg.replace("#question","").strip())

            elif len(mesg) != len(mesg.replace("#clarify", "")):
                res = _agent.clarification_questions(query=mesg.replace("#clarify","").strip())

            elif len(mesg) != len(mesg.replace("#explain", "")):
                res = _agent.explain()

            elif len(mesg) != len(mesg.replace("#rephrasing","")):
                res = _agent.rephrase_query(query=mesg.replace("#rephrasing","").strip())

            else:
                res = _agent.chat(query=mesg.strip())


            page.pubsub.send_all(
                Message("Agent", res, message_type="chat_message"))
            page.update()



    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message,page)

        chat.controls.append(m)
        page.update()

        if message.user_name == "You":
            to_agent(message)



    page.pubsub.subscribe(on_message)


    def on_file_selected(e):
            #print(e.files)
            if len(e.files) > 0:
                fobj = e.files[0]
                fp = pd.read_excel(fobj.path)
                df = pd.DataFrame(fp)
                page.dialog.open = False
                page.update()
                _agent = Agent([df], config={"llm": llm})
                page.session.set("agent",_agent);
                #print(_agent)
                join_chat()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.add(file_picker)

    def pick_file_to_process(e):
            file_picker.pick_files(allow_multiple=False,allowed_extensions=["xlsx"],dialog_title="Select the file")




    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Select Excel file"),
        #content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Choose file", on_click=pick_file_to_process)],
        actions_alignment="end",
    )


    def on_resize(event):
            page.session.set("pageWidth",page.width)


    page.on_resize = on_resize;

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    # Add everything to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )

ft.app(target=main)
