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

    content_area=ft.Column(expand=True)

    word_input=ft.TextField(label="Word",autofocus=True,expand=True)
    meaning_input=ft.TextField(label="Meaning",expand=True,multiline=True,min_lines=4,max_lines=4,)
    tag_input=ft.TextField(label="Tags",expand=True,on_change=lambda e:update_tag_suggestions(e.value))
    tag_suggestions=ft.Column()
    selected_tags=[]


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
                        ft.Row([meaning_input]),
                        ft.Row([tag_input]),
                        tag_suggestions,
                        ft.ElevatedButton("Save",on_click=save_word)
                        ])
                    )
        if view_name=="list":
            content_area.controls.append(ft.Text("List Page"))
        if view_name=="config":
            content_area.controls.append(ft.Text("Config Page"))
        if page.drawer.open:
            open_drawer(None)
        page.update()

    def open_drawer(e):
        page.drawer.open=not page.drawer.open
        page.update()


    def on_keypress(e:ft.KeyboardEvent):
        if e.key=="Escape":
            page.window.visible=False
            page.window.destroy()
        elif e.alt and e.key=="Enter":
            save_word(None)

    page.drawer=ft.NavigationDrawer(
            controls=[
                ft.Text("Navigation",size=16,weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ListTile(title=ft.Text("Main Page"),on_click=lambda e:update_content("main")),
                ft.ListTile(title=ft.Text("List Page"),on_click=lambda e:update_content("list")),
                ft.ListTile(title=ft.Text("Config Page"),on_click=lambda e:update_content("config")),
                ]
            )

    page.add(
            ft.Column([
                ft.Container(
                    ft.Row([
                        ft.IconButton(ft.icons.MENU,on_click=open_drawer),
                        content_area,
                        ],alignment=ft.alignment.top_left),
                    padding=10,
                    width=550,
                    height=50,
                    ),
                ])
            )
    
    update_content("main")
    update_tag_suggestions("")
    page.on_keyboard_event=on_keypress

ft.app(target=main)


