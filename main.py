import flet as ft
import json
DATA_FILE="data/words.json"

def load_words():
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError,json.JSONDecodeError):
        return []

def save_words(words):
    with open(DATA_FILE,"w",encoding="utf-8") as file:
        json.dump(words,file,indent=4,ensure_ascii=False)

def main(page:ft.Page):
    page.title="Words Stacker"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.window.width=600
    page.window.height=400
    page.window.resizable=False

    content_area=ft.Column(width=500)

    word_input=ft.TextField(label="Word",autofocus=True,expand=True)
    meaning_input=ft.TextField(label="Meaning",expand=True,multiline=True,min_lines=8,max_lines=8,)
    tag_input=ft.TextField(label="Tags",expand=True,on_change=lambda e:update_tag_suggestions(e.value))
    tag_suggestions=ft.Column()
    selected_tags=[]

    def open_drawer(e):
        page.drawer.open=not page.drawer.open
        page.update()

    def update_tag_suggestions(query):
        tag_suggestions.controls.clear()
        if query:
            matching_tags=[t for t in TAGS if t.startswith(query)]
            for tag in matching_tags:
                tag_suggestions.controls.append(
                        ft.TextButton(tag,on_click=lambda e,t=tag:select_tag(t))
                        )
        page.update()

    def select_tag(tag):
        if tag not in selected_tags:
            selected_tags.append(tag)
        tag_input.value=" ".join(selected_tags)
        tag_suggestions.controls.clear()
        page.update()


    def save_word(e):
        if word_input.value and meaning_input.value:
            new_entry={"word": word_input.value,"meaning":meaning_input.value,"tags":selected_tags}
            words=load_words()
            words.append(new_entry)
            save_words(words)
            word_input.value=""
            meaning_input.value=""
            tag_input.value=""
            selected_tags.clear()
            word_input.focus()
            page.update()

    def update_content(view_name):
        content_area.controls.clear()
        if view_name=="main":
            content_area.controls.append(
                    ft.Column([
                        ft.Row([word_input]),
                        ft.Row([tag_input]),
                        ft.Row([meaning_input]),
                        tag_suggestions,
                        #ft.ElevatedButton("Save",on_click=save_word)
                        ])
                    )
        if view_name=="list":
            content_area.controls.append(ft.Text("List Page"))
        if view_name=="config":
            content_area.controls.append(ft.Text("Config Page"))
        if page.drawer.open:
            open_drawer(None)
        page.update()



    def on_keypress(e:ft.KeyboardEvent):
        if e.key=="Escape":
            print("EXITTTTTTTTTTTTT")
            page.window.visible=False
            page.window.destroy()
        elif e.alt and e.key=="Enter":
            save_word(None)

    page.drawer=ft.NavigationDrawer(
            controls=[
                ft.Text("   Menu",size=16,weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ListTile(title=ft.Text("Main Page"),on_click=lambda e:update_content("main")),
                ft.ListTile(title=ft.Text("List Page"),on_click=lambda e:update_content("list")),
                ft.ListTile(title=ft.Text("Config Page"),on_click=lambda e:update_content("config")),
                ]
            )


    page.add(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            margin=ft.Margin(top=0,right=0,left=0,bottom=290),
                            content=ft.Column([ft.IconButton(ft.Icons.MENU,on_click=open_drawer)])
                            ),
                        content_area,
                    ]
                ),
                border_radius=10,
                #bgcolor=ft.Colors.AMBER,
            )
        )


    update_content("main")
    update_tag_suggestions("")
    page.on_keyboard_event=on_keypress

ft.app(target=main)


