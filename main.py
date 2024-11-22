import flet as ft
import base64
from PIL import Image
import io
import os

MAX_SIZE = 75 * 1024  # 75 Кб


def encode_image(file_path):
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string
    except Exception as e:
        return f"Помилка: {e}"


def decode_image(encoded_string, save_path):
    try:
        image_data = base64.b64decode(encoded_string)
        with open(save_path, "wb") as image_file:
            image_file.write(image_data)
        return True
    except Exception as e:
        return f"Помилка: {e}"


def compress_image(file_path):
    img = Image.open(file_path)
    img_format = img.format

    quality = 95
    while True:
        img_io = io.BytesIO()
        img.save(img_io, format=img_format, quality=quality)
        img_size = img_io.tell()
        if img_size <= MAX_SIZE or quality <= 10:
            break
        quality -= 5

    img_io.seek(0)
    return img_io


def main(page: ft.Page):
    page.title = "Кодування/Декодування Зображень у Base64"
    page.horizontal_alignment = "center"

    # Tabs
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Кодування"),
            ft.Tab(text="Декодування"),
        ],
        expand=1,
    )

    # Кодування
    encode_file_path = ft.TextField(label="Вибраний файл", read_only=True, expand=1)
    encode_image_preview = ft.Image(height=200)
    encode_base64_output = ft.TextField(
        label="Base64 результат", multiline=True, read_only=True, expand=1
    )

    def pick_file(e):
        file_picker.pick_files(allow_multiple=False)

    def on_file_selected(e):
        if file_picker.result is None or len(file_picker.result.files) == 0:
            return
        file_path = file_picker.result.files[0].path
        encode_file_path.value = file_path

        # Перевірка розміру файлу
        file_size = os.path.getsize(file_path)
        if file_size > MAX_SIZE:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Розмір файлу перевищує {MAX_SIZE // 1024} Кб. Виконайте стиснення.")
            )
            page.snack_bar.open()
            compress_button.disabled = False
        else:
            compress_button.disabled = True
            convert_button.disabled = False

        # Відображення зображення
        img = Image.open(file_path)
        img.thumbnail((200, 200))
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")
        encode_image_preview.src_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")
        page.update()

    def convert_image(e):
        if not encode_file_path.value:
            return
        encoded_str = encode_image(encode_file_path.value)
        if encoded_str:
            encode_base64_output.value = encoded_str
            page.snack_bar = ft.SnackBar(ft.Text("Кодування виконано успішно."))
            page.snack_bar.open()
        page.update()

    def compress_and_convert(e):
        if not encode_file_path.value:
            return
        compressed_img = compress_image(encode_file_path.value)
        compressed_path = encode_file_path.value.replace(".", "_compressed.")
        with open(compressed_path, "wb") as f:
            f.write(compressed_img.getvalue())
        encode_file_path.value = compressed_path
        convert_image(e)

    # Buttons
    file_picker = ft.FilePicker(on_result=on_file_selected)
    convert_button = ft.ElevatedButton("Конвертувати", on_click=convert_image, disabled=True)
    compress_button = ft.ElevatedButton(
        "Стиснути та конвертувати", on_click=compress_and_convert, disabled=True
    )
    page.overlay.append(file_picker)

    # Layout
    encode_tab_content = ft.Column(
        [
            ft.Row([encode_file_path, ft.IconButton(ft.icons.FOLDER, on_click=pick_file)]),
            encode_image_preview,
            ft.Row([convert_button, compress_button]),
            encode_base64_output,
        ],
        expand=1,
    )

    # Декодування
    decode_text_input = ft.TextField(label="Base64 текст", multiline=True, expand=1)
    decoded_image_preview = ft.Image(height=200)

    def decode_base64(e):
        if not decode_text_input.value.strip():
            return
        decoded_img_path = "decoded_image.png"
        result = decode_image(decode_text_input.value.strip(), decoded_img_path)
        if result is True:
            img = Image.open(decoded_img_path)
            img.thumbnail((200, 200))
            img_io = io.BytesIO()
            img.save(img_io, format="PNG")
            decoded_image_preview.src_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text(result))
            page.snack_bar.open()

    decode_button = ft.ElevatedButton("Декодувати", on_click=decode_base64)

    decode_tab_content = ft.Column(
        [
            decode_text_input,
            decode_button,
            decoded_image_preview,
        ],
        expand=1,
    )

    # Tabs content
    tabs.content = [encode_tab_content, decode_tab_content]

    page.add(tabs)


ft.app(target=main)
