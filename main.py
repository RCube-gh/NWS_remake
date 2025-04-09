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
    page.window.resizable=True
    page.bgcolor=ft.Colors.BLUE_100

    TAGS=load_tags()
    #content_area=ft.Column(width=page.window.width-130,expand=True)
    content_area=ft.Column(expand=True)
    main_title=ft.Text(
        "Words Stacker",
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_900,
        text_align=ft.TextAlign.CENTER,
    )

    word_input=ft.TextField(
        label="Word",
        autofocus=True,
        expand=True,
        text_size=24,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.WHITE70,
    )
    meaning_input=ft.TextField(
        label="Meaning",
        expand=True,
        multiline=True,
        min_lines=800,
        max_lines=800,
        text_size=16,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.WHITE70,
    )
    tag_input=ft.TextField(
        label="Tags",
        expand=True,
        on_change=lambda e:update_tag_suggestions(tag_input.value),
        on_submit=lambda e: add_tag(tag_input.value),
        bgcolor=ft.Colors.WHITE70,
    )
    selected_tags_view=ft.Row(wrap=True,spacing=5)
    selected_tags=[]
    suggestions_box = ft.Container(
        content=ft.Column(spacing=0),
        bgcolor=ft.Colors.GREY_100,
        border=ft.border.all(1, ft.Colors.GREY_700),
        border_radius=5,
        padding=5,
        visible=False,
        width=300,
        animate_opacity=100,
        shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK26),
        opacity=0
    )

    search_input=ft.TextField(
        label="Search",
        hint_text="Search for words or meanings",
        #expand=True,
        width=350,
        text_size=16,
        bgcolor=ft.Colors.WHITE70,
        on_change=lambda e: handle_search()
    )


    table_container=None

    def on_resize(e):
        #print("Resizing")
        #update_content("list")
        if table_container:
            table_container.height=page.window.height-210
            page.update()


    def open_drawer(e):
        page.drawer.open=not page.drawer.open
        page.update()
    


    def word_detail_modal(word_obj):
        word_field=ft.TextField(
            value=word_obj["word"],
            label="Word",
            read_only=True,
            bgcolor=ft.Colors.WHITE70,
            text_size=24,
        )
        meaning_field=ft.TextField(
            value=word_obj["meaning"],
            label="Meaning",
            multiline=True,
            read_only=True,
            bgcolor=ft.Colors.WHITE70,
        )
        tag_field=ft.TextField(
            value=", ".join(word_obj.get("tags", [])),
            label="Tags",
            read_only=True,
            bgcolor=ft.Colors.WHITE70,
        )
        edit_mode=ft.Ref[bool]()
        edit_mode.current=False
        edit_label=ft.Ref[ft.Text]()
        def toggle_edit(e):
            edit_mode.current=not edit_mode.current
            word_field.read_only=not edit_mode.current
            meaning_field.read_only=not edit_mode.current
            tag_field.read_only=not edit_mode.current
            if edit_label.current:
                edit_label.current.visible=edit_mode.current
            page.update()
        def save_word_update(updated_entry):
            words=load_words()
            for i,w in enumerate(words):
                if w["created_at"]==updated_entry["created_at"]:
                    words[i]=updated_entry
                    break
            save_words(words)
            handle_search()


        def save_changes(e):
            updated_word=word_field.value.strip()
            updated_meaning=meaning_field.value.strip()
            updated_tags=[t.strip() for t in tag_field.value.split(",") if t.strip()]
            word_obj["word"]=updated_word  
            word_obj["meaning"]=updated_meaning
            word_obj["tags"]=updated_tags
            save_word_update(word_obj)
            
            page.snack_bar=ft.SnackBar(
                content=ft.Text("✅ Word updated successfully!",size=20,color=ft.Colors.GREEN_900),
                #duration=ft.Duration(seconds=0.5),
                duration=2000,
                bgcolor=ft.Colors.GREEN_50,
            )
            page.open(page.snack_bar)
            page.update()
            page.close(modal)



        def confirm_delete(e):
            def close_delete_confirm_modal(e):
                page.close(delete_confirm_modal)
                page.update()
            def delete_word(entry):
                words=load_words()
                words=[w for w in words if w["created_at"]!=entry["created_at"]]
                save_words(words)
                handle_search() #refresh the list view
                page.snack_bar=ft.SnackBar(
                    content=ft.Text("✅ Word deleted successfully!",size=20,color=ft.Colors.GREEN_900),
                    duration=2000,
                    bgcolor=ft.Colors.GREEN_50,
                )
                page.open(page.snack_bar)
                page.update()
                page.close(delete_confirm_modal)
            delete_confirm_modal=ft.AlertDialog(
                modal=True,
                title=ft.Text("Delete this word??"),
                content=ft.Text("Are you sure you want to delete this entry?"),
                actions=[
                    ft.TextButton("Cancel",on_click=lambda e:close_delete_confirm_modal(e)),
                    ft.TextButton("Delete",on_click=lambda e:delete_word(word_obj)),
                ]
            )
            page.dialog=delete_confirm_modal
            page.open(delete_confirm_modal)
        modal=ft.AlertDialog(
            title=ft.Row([
                ft.Text("Word Details",size=32,weight=ft.FontWeight.BOLD),
                ft.Text("(editing)",ref=edit_label,color=ft.Colors.BLACK54,visible=False,size=20),
            ]),
            content=ft.Container(
                    content=ft.Column([
                        word_field,
                        meaning_field,
                        tag_field,
                        ft.Container(
                            content=ft.Text(f"Date Added: {word_obj[('created_at')].split('T')[0]}",italic=True,size=12,color=ft.Colors.GREY_900),
                            alignment=ft.alignment.center_right,
                        )
                    ],spacing=10),
                    width=page.window.width-300,
                    padding=20,
                    border_radius=10,
                    animate_opacity=100,
            ),
            actions=[
                #ft.TextButton("Save",on_click=save_changes,disabled=not edit_mode.current),
                ft.TextButton("Edit",on_click=toggle_edit),
                ft.TextButton("Delete",on_click=confirm_delete),
                ft.TextButton("Save",on_click=save_changes),
                ft.TextButton("Close",on_click=lambda e:page.close(modal)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            content_padding=10,
            bgcolor=ft.Colors.BLUE_50,
            shape=ft.RoundedRectangleBorder(radius=30),
        )
        page.dialog=modal
        page.open(modal)
    
    
    def update_list_view(words):
        nonlocal table_container
        data_rows=[]
        if not words:
            table_container.content.controls.clear()
            table_container.content.controls.append(ft.Text("No words found",italic=True,color=ft.Colors.GREY_500))
            page.update()
            return
        for w in reversed(words):
            row=ft.Row([
                ft.Text(w["word"], expand=1),
                ft.Text(
                    w["meaning"],
                    expand=2,
                    max_lines=3,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    tooltip=w["meaning"]
                ),
                ft.Text(", ".join(w.get("tags", [])), expand=1, max_lines=2),
                ft.Text(w["created_at"].split("T")[0], width=100),
            ], spacing=10)
            data_rows.append(
                ft.Container(
                    content=row,
                    on_click=lambda e,word=w: word_detail_modal(word),
                    on_long_press=lambda e,word=w: word_detail_modal(word),
                    padding=10,
                    ink=True,
                    border_radius=5,
                    bgcolor=ft.Colors.TRANSPARENT,
                )
            )

        if table_container:
            table_container.content.controls=data_rows
            page.update()

    def parse_search_query(query):
        import re
        include_tag_pattern=r"(?<!-)\#(\w+)"
        exclude_tag_pattern=r"-\#(\w+)"
        phrase_pattern=r'"([^"]+)"'
        include_tags=re.findall(include_tag_pattern,query)
        exclude_tags=re.findall(exclude_tag_pattern,query)
        phrases=re.findall(phrase_pattern,query)
        clean_query=re.sub(include_tag_pattern,"",query)
        clean_query=re.sub(exclude_tag_pattern,"",clean_query)
        clean_query=re.sub(phrase_pattern,"",clean_query)
        keywords=clean_query.strip().split()
        return{
            "include_tags":include_tags,
            "exclude_tags":exclude_tags,
            "phrases":phrases,
            "keywords":keywords
        }



    def handle_search():
        nonlocal table_container
        q=parse_search_query(search_input.value.lower())
        include_tags=q["include_tags"]
        exclude_tags=q["exclude_tags"]
        phrases=q["phrases"]
        keywords=q["keywords"]

        filtered=[]

        print("======================")
        print("Searching for:")
        print("Include Tags:",include_tags)
        print("Exclude Tags:",exclude_tags)
        print("Phrases:",phrases)
        print("Keywords:",keywords)

        query_exists=bool(keywords or phrases or include_tags or exclude_tags)



        for w in load_words():
            word_tags=[t.lower() for t in w.get("tags",[])]
            text=(w["word"]+" "+w["meaning"]).lower()
            text_match=(
                any(k in text for k in keywords) or
                any(p in text for p in phrases)
            )
            include_match=all(tag in word_tags for tag in include_tags)
            exclude_match=all(tag not in word_tags for tag in exclude_tags)
            if not query_exists:
                filtered.append(w)
            elif (text_match and include_match and exclude_match) or (not keywords and not phrases and include_match and exclude_match):
                filtered.append(w)
            

        update_list_view(filtered)
        
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
                        bgcolor=ft.Colors.WHITE,
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
        if word_input.value:
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
        nonlocal table_container
        content_area.controls.clear()
        if view_name=="main":
            content_area.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Column([
                                ft.Row([main_title],alignment=ft.MainAxisAlignment.CENTER),
                                #ft.Divider(),
                                word_input,
                                selected_tags_view,
                                ft.Column([tag_input,suggestions_box]),
                            ],spacing=10),
                            ft.Container(
                                content=meaning_input,
                                expand=True,
                            ),
                        ],
                    #expand=True
                    ),expand=True,
                ),
            )
        elif view_name=="list":
            words = load_words()

            # HEADER ROW
            header_row = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Word", weight=ft.FontWeight.BOLD, expand=1),
                        ft.Text("Meaning", weight=ft.FontWeight.BOLD, expand=2),
                        ft.Text("Tags", weight=ft.FontWeight.BOLD, expand=1),
                        ft.Text("Date", weight=ft.FontWeight.BOLD, width=100)
                    ], spacing=0),
                    ft.Divider(color=ft.Colors.BLUE_500, thickness=2),
                ]),
                bgcolor=ft.Colors.BLUE_50,
                padding=0
            )

            # DATA ROWS
            # TABLE WRAPPER
            table_container = ft.Container(
                content=ft.Column([], scroll="auto", spacing=8),
                height=page.window.height - 200,
                expand=True
            )


            content_area.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("📑 Word List", size=28, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Row(
                                            [search_input],
                                            spacing=10,
                                            alignment=ft.MainAxisAlignment.END
                                        ),
                                        expand=True,
                                        #alignment=ft.alignment.center_right
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),

                            ft.Container(
                                content=ft.Column([
                                    header_row,
                                    table_container
                                ]),
                                bgcolor=ft.Colors.WHITE,
                            )
                        ],
                            spacing=15,
                            expand=True
                        ),
                        expand=True,
                    padding=10,
                )
            )
            update_list_view(words)
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
                    bgcolor=ft.Colors.BLUE_200,
                    width=60,  # fixed width menu
                    padding=10
                ),
                
                # Main Content Area (expand to fill)
                ft.Container(
                    content=content_area,
                    expand=True,
                    padding=10,
                    margin=ft.margin.only(left=10, right=40, top=0, bottom=10),
                ),
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START  # aligns children vertically at the top
        )
    )


    page.on_keyboard_event=on_keypress
    update_content("main")
    update_tag_suggestions("")
    page.on_resized=on_resize
ft.app(target=main)