import flet as ft
import base64
from PIL import Image
import io
import os

MAX_SIZE = 75 * 1024  # Ліміт розміру файлу (75 КБ)

def main(page: ft.Page):
    # UI елементи
    page.title = "Base64 Encoder/Decoder"
    page.scroll = "auto"
    page.padding = 20

    selected_file = ft.Text(value="No file selected", size=14)
    base64_output = ft.TextField(label="Base64 Output", multiline=True, expand=True)
    decode_input = ft.TextField(label="Base64 Input", multiline=True, expand=True)
    image_preview = ft.Image(width=200, height=200, fit="contain")

    def encode_image(file_path):
        """Кодує зображення у Base64."""
        try:
            with open(file_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            ft.MessageBox("Error", str(e), icon=ft.AlertType.ERROR).show()

    def decode_image(base64_string):
        """Декодує Base64 у зображення."""
        try:
            image_data = base64.b64decode(base64_string)
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            ft.MessageBox("Error", str(e), icon=ft.AlertType.ERROR).show()

    def on_file_picker_result(e: ft.FilePickerResultEvent):
        """Обробка вибору файлу."""
        if e.files:
            file_path = e.files[0].path
            selected_file.value = file_path
            page.update()
            
            # Перевірка розміру файлу
            file_size = os.path.getsize(file_path)
            if file_size > MAX_SIZE:
                ft.MessageBox(
                    "File too large",
                    f"File size {file_size // 1024} KB exceeds limit of 75 KB. Compress the image before encoding.",
                    icon=ft.AlertType.WARNING
                ).show()
                return
            
            # Показ прев'ю зображення
            with Image.open(file_path) as img:
                img.thumbnail((200, 200))
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                image_preview.src_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                page.update()

    def encode_button_click(e):
        """Кодує зображення у Base64."""
        if not selected_file.value or selected_file.value == "No file selected":
            ft.MessageBox("Error", "No file selected!", icon=ft.AlertType.ERROR).show()
            return
        
        encoded_str = encode_image(selected_file.value)
        if encoded_str:
            base64_output.value = encoded_str
            page.update()

    def decode_button_click(e):
        """Декодує Base64 у зображення."""
        if not decode_input.value.strip():
            ft.MessageBox("Error", "No Base64 input provided!", icon=ft.AlertType.ERROR).show()
            return
        
        try:
            decoded_image = decode_image(decode_input.value)
            buf = io.BytesIO()
            decoded_image.thumbnail((200, 200))
            decoded_image.save(buf, format="PNG")
            image_preview.src_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            page.update()
        except Exception as ex:
            ft.MessageBox("Error", str(ex), icon=ft.AlertType.ERROR).show()

    # Файл-пікер
    file_picker = ft.FilePicker(on_result=on_file_picker_result)

    # Додавання елементів до сторінки
    page.overlay.append(file_picker)
    page.add(
        ft.Row(
            controls=[
                ft.ElevatedButton("Select File", on_click=lambda _: file_picker.pick_files()),
                selected_file,
            ],
        ),
        ft.Row(
            controls=[
                ft.ElevatedButton("Encode to Base64", on_click=encode_button_click),
                ft.ElevatedButton("Decode Base64", on_click=decode_button_click),
            ],
        ),
        base64_output,
        decode_input,
        image_preview,
    )

# Запуск Flet-додатка
if __name__ == "__main__":
    ft.app(target=main)
