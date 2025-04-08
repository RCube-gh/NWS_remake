import flet as ft
import json
import os
from datetime import datetime


os.makedirs("data",exist_ok=True)
DATA_FILE="data/words.json"
TAGS_FILE="data/tags.json"
def load_words():
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError,json.JSONDecodeError):
        return []

def save_words(words):
    with open(DATA_FILE,"w",encoding="utf-8") as file:
        json.dump(words,file,indent=4,ensure_ascii=False)

def load_tags():
    try:
        with open(TAGS_FILE,"r",encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError,json.JSONDecodeError):
        return []

def save_tags(tags):
    with open(TAGS_FILE,"w",encoding="utf-8") as file:
        json.dump(tags,file,indent=4,ensure_ascii=False)



def main(page:ft.Page):
    page.title="Words Stacker"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.window.width=800
    page.window.height=540
    page.window.resizable=False
    page.bgcolor=ft.colors.BLUE_100

    TAGS=load_tags()
    content_area=ft.Column(width=page.window.width-130)
    main_title=ft.Text(
        "Words Stacker",
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.BLUE_900,
        text_align=ft.TextAlign.CENTER,
    )

    word_input=ft.TextField(
        label="Word",
        autofocus=True,
        expand=True,
        text_size=24,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        bgcolor=ft.colors.WHITE70,
    )
    meaning_input=ft.TextField(
        label="Meaning",
        expand=True,
        multiline=True,
        min_lines=8,
        max_lines=8,
        text_size=16,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        bgcolor=ft.colors.WHITE70,
    )
    tag_input=ft.TextField(
        label="Tags",
        expand=True,
        on_change=lambda e:update_tag_suggestions(tag_input.value),
        on_submit=lambda e: add_tag(tag_input.value),
        bgcolor=ft.colors.WHITE70,
    )
    selected_tags_view=ft.Row(wrap=True,spacing=5)
    selected_tags=[]
    suggestions_box = ft.Container(
        content=ft.Column(spacing=0),
        bgcolor=ft.colors.GREY_100,
        border=ft.border.all(1, ft.colors.GREY_700),
        border_radius=5,
        padding=5,
        visible=False,
        width=300,
        animate_opacity=100,
        shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.BLACK26),
        opacity=0
    )

    def open_drawer(e):
        page.drawer.open=not page.drawer.open
        page.update()

    def update_tag_suggestions(query):
        suggestions_box.content.controls.clear()
        matched = [tag for tag in TAGS if query.lower() in tag.lower() and tag not in selected_tags]
        if query and matched:
            for tag in matched:
                suggestions_box.content.controls.append(
                    ft.Container(
                        content=ft.TextButton(
                            tag,
                            on_click=lambda e, t=tag: add_tag(t),
                            width=suggestions_box.width-10,
                        ),
                        padding=0,
                        bgcolor=ft.colors.WHITE,
                        border_radius=5,
                    )
                )
            suggestions_box.visible = True
            suggestions_box.opacity = 1
        else:
            suggestions_box.visible = False
            suggestions_box.opacity = 0
        page.update()

    def add_tag(tag):
        tag = tag.strip()
        if tag and tag not in selected_tags:
            selected_tags.append(tag)
            selected_tags_view.controls.append(
                ft.Chip(label=ft.Text(tag), on_delete=lambda e, t=tag: remove_tag(t))
            )
        tag_input.value = ""
        suggestions_box.visible = False
        suggestions_box.opacity = 0
        tag_input.focus()
        page.update()

    def remove_tag(tag):
        selected_tags.remove(tag)
        selected_tags_view.controls.clear()
        for t in selected_tags:
            selected_tags_view.controls.append(
                ft.Chip(label=ft.Text(t), on_delete=lambda e, t=t: remove_tag(t))
            )
        page.update()

    def save_word(e):
        if word_input.value and meaning_input.value:
            new_entry={
                "word": word_input.value,
                "meaning":meaning_input.value,
                "tags":selected_tags,
                "created_at":datetime.now().isoformat()
            }
            words=load_words()
            words.append(new_entry)
            save_words(words)
            #save new tags to file
            existing_tags=load_tags()
            for tag in selected_tags:
                if tag not in existing_tags:
                    existing_tags.append(tag)
            save_tags(existing_tags)
            TAGS[:] = existing_tags

            word_input.value=""
            meaning_input.value=""
            tag_input.value=""
            selected_tags.clear()
            selected_tags_view.controls.clear()
            word_input.focus()
            page.update()

    def update_content(view_name):
        content_area.controls.clear()
        if view_name=="main":
            content_area.controls.append(
                    ft.Column([
                        ft.Row([main_title],alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([word_input]),
                        selected_tags_view,
                        ft.Column([tag_input,suggestions_box]),
                        ft.Row([meaning_input]),
                        #ft.ElevatedButton("Save",on_click=save_word)
                        ])
                    )
        elif view_name=="list":
            if not load_words():
                content_area.controls.append(ft.Text("No words found"))
                if page.drawer.open:
                    open_drawer(None)
                page.update()
                return
            table=ft.DataTable(
                columns=[
                    ft.DataColumn(label=ft.Text("Word")),
                    ft.DataColumn(label=ft.Text("Meaning")),
                    ft.DataColumn(label=ft.Text("Tags")),
                    ft.DataColumn(label=ft.Text("Date")),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(w["word"], weight=ft.FontWeight.BOLD, max_lines=1, no_wrap=True,width=150)),
                            ft.DataCell(ft.Text(w["meaning"], max_lines=3, overflow=ft.TextOverflow.ELLIPSIS, tooltip=w["meaning"],width=200)),
                            ft.DataCell(ft.Text(", ".join(w.get("tags", [])), max_lines=2,width=150)),
                            ft.DataCell(ft.Text(w["created_at"].split("T")[0],width=100)),
                        ]
                    )
                    for w in reversed(load_words())
                ],
                heading_row_color=ft.colors.BLUE_500,
                column_spacing=10,
                divider_thickness=1,
                bgcolor=ft.colors.BLUE_50,
            )

            content_area.controls.append(
                ft.Column([
                    ft.Text("📑 Word Table", size=28, weight=ft.FontWeight.BOLD),
                    table
                ])
            )
        elif view_name=="config":
            content_area.controls.append(ft.Text("Config Page"))
        if page.drawer.open:
            open_drawer(None)
        page.update()



    def on_keypress(e:ft.KeyboardEvent):
        if e.key=="Escape":
            page.window.close()
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
        ft.Row(
            [
                # Left Menu (fixed width)
                ft.Container(
                    content=ft.Column(
                        [ft.IconButton(ft.Icons.MENU, on_click=open_drawer)],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    bgcolor=ft.colors.BLUE_200,
                    width=60,  # fixed width menu
                    padding=10
                ),
                
                # Main Content Area (expand to fill)
                ft.Container(
                    content=content_area,
                    expand=True,
                    padding=10,
                ),
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START  # aligns children vertically at the top
        )
    )


    page.on_keyboard_event=on_keypress
    update_content("main")
    update_tag_suggestions("")

ft.app(target=main)