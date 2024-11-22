import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import base64
import os
from PIL import Image, ImageTk
import io

MAX_SIZE = 75 * 1024  # 75 Кб

def encode_image(file_path):
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося закодувати зображення:\n{e}")
        return None

def decode_image(encoded_string, save_path):
    try:
        image_data = base64.b64decode(encoded_string)
        with open(save_path, "wb") as image_file:
            image_file.write(image_data)
        return True
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося декодувати зображення:\n{e}")
        return False

class Application(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Кодування/Декодування Зображень у Base64")
        self.geometry("690x455")
        self.minsize(300, 200)
        self.resizable(True, True)

        self.encode_image_path = tk.StringVar()
        self.encode_size = None  # Додано для зберігання розміру файлу

        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.encode_tab = ttk.Frame(self.tab_control)
        self.decode_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.encode_tab, text='Кодування')
        self.tab_control.add(self.decode_tab, text='Декодування')

        self.create_encode_tab()
        self.create_decode_tab()

    def create_encode_tab(self):
        frame = ttk.Frame(self.encode_tab)
        frame.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        lbl = ttk.Label(frame, text="Виберіть або перетягніть зображення для кодування:")
        lbl.grid(row=0, column=0, sticky="w")

        self.encode_drop_area = tk.Label(
            self.encode_tab, text="Перетягніть файл сюди", relief="groove"
        )
        self.encode_drop_area.grid(row=1, column=0, pady=25, padx=25, ipadx=5, ipady=75, sticky="nsew")

        self.encode_image_label = ttk.Label(self.encode_tab)
        self.encode_image_label.grid(row=1, column=1, padx=5, sticky="nsew")

        self.encode_drop_area.drop_target_register(DND_FILES)
        self.encode_drop_area.dnd_bind('<<Drop>>', self.on_drop_encode)

        btn = ttk.Button(frame, text="Вибрати файл", command=self.browse_encode_file)
        btn.grid(row=0, column=1, padx=5, sticky="w")

        lbl_b64 = ttk.Label(self.encode_tab, text="Base64 формат:")
        lbl_b64.grid(row=2, column=0, sticky="w", padx=5)

        self.encode_text = scrolledtext.ScrolledText(self.encode_tab, height=5)
        self.encode_text.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")

        btn_frame = ttk.Frame(self.encode_tab)
        btn_frame.grid(row=4, column=1, pady=5, padx=5, sticky="e")

        self.convert_btn = ttk.Button(btn_frame, text="Конвертувати", command=self.convert_image, state="disabled", width=15)
        self.convert_btn.grid(row=0, column=0, padx=5)

        self.compress_btn = ttk.Button(btn_frame, text="Стиснути", command=self.compress_image, state="disabled", width=15)
        self.compress_btn.grid(row=0, column=1, padx=5)

        copy_btn = ttk.Button(btn_frame, text="Копіювати текст", command=self.copy_encode_text, state="disabled", width=15)
        copy_btn.grid(row=1, column=0, padx=5)

        clear_btn = ttk.Button(btn_frame, text="Очистити вміст", command=self.clear_encode_text, width=15)
        clear_btn.grid(row=1, column=1, padx=5)

        self.copy_btn = copy_btn  # Зберігаємо посилання на кнопку Копіювати текст

    def create_decode_tab(self):
        self.decode_tab.grid_rowconfigure(1, weight=1)
        self.decode_tab.grid_columnconfigure(0, weight=1)

        frame = ttk.Frame(self.decode_tab)
        frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        lbl = ttk.Label(frame, text="Вставте Base64 текст для декодування:")
        lbl.grid(row=0, column=0, sticky="w")

        self.decode_text = scrolledtext.ScrolledText(frame, height=15)
        self.decode_text.grid(row=1, column=0, pady=5, sticky="nsew")

        paste_btn = ttk.Button(frame, text="Вставити з буфера", command=self.paste_text)
        paste_btn.grid(row=2, column=0, pady=5, sticky="ew")

        decode_btn = ttk.Button(frame, text="Декодувати та зберегти зображення", command=self.decode_action)
        decode_btn.grid(row=3, column=0, pady=5, sticky="ew")

    def paste_text(self):
        try:
            text = self.clipboard_get()
            self.decode_text.insert(tk.END, text)
        except tk.TclError:
            messagebox.showwarning("Попередження", "Немає тексту в буфері обміну.")

    def browse_encode_file(self):
        file_path = filedialog.askopenfilename(
            title="Виберіть зображення",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            self.process_encode_file(file_path)

    def on_drop_encode(self, event):
        file_path = event.data
        if self.tk.splitlist(file_path):
            file_path = self.tk.splitlist(file_path)[0]
            file_path = file_path.strip('{}')
            if os.path.isfile(file_path):
                self.process_encode_file(file_path)

    def process_encode_file(self, file_path):
        self.encode_image_path.set(file_path)

        # Перевірка розміру файлу
        file_size = os.path.getsize(file_path)
        self.encode_size = file_size  # Зберігаємо розмір файлу для подальшої обробки
        if file_size > MAX_SIZE:
            self.convert_btn.config(state="disabled")
            self.compress_btn.config(state="normal")
            self.copy_btn.config(state="disabled")
            messagebox.showwarning(
                "Розмір файлу перевищено",
                f"Розмір зображення {file_size // 1024} Кб перевищує ліміт у 75 Кб. Використовуйте кнопку 'Стиснути'."
            )
            return
        else:
            self.convert_btn.config(state="normal")
            self.compress_btn.config(state="disabled")

        try:
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            self.photo = ImageTk.PhotoImage(img)
            self.encode_image_label.config(image=self.photo)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відобразити зображення:\n{e}")
            self.encode_image_label.config(image='')

    def convert_image(self):
        file_path = self.encode_image_path.get()
        if file_path:
            encoded_str = encode_image(file_path)
            if encoded_str:
                self.encode_text.delete('1.0', tk.END)
                self.encode_text.insert(tk.END, encoded_str)
                self.copy_btn.config(state="normal")  # Активуємо кнопку Копіювати текст

    def compress_image(self):
        file_path = self.encode_image_path.get()
        if file_path:
            img = Image.open(file_path)
            img_format = img.format
            
            # Стискаємо зображення до 75 Кб
            quality = 95
            while True:
                img_io = io.BytesIO()
                img.save(img_io, format=img_format, quality=quality)
                img_size = img_io.tell()
                if img_size <= MAX_SIZE or quality <= 10:
                    break
                quality -= 5
            
            compressed_path = filedialog.asksaveasfilename(
                defaultextension=f".{img_format.lower()}",
                filetypes=[(f"{img_format.upper()} files", f"*.{img_format.lower()}")],
                title="Зберегти стиснуте зображення як"
            )
            
            if compressed_path:
                img_io.seek(0)
                with open(compressed_path, "wb") as f:
                    f.write(img_io.read())
                
                messagebox.showinfo("Успіх", f"Зображення стиснуто та збережено за адресою:\n{compressed_path}")
                self.process_encode_file(compressed_path)  # Автоматично обробляємо стиснуте зображення

    def copy_encode_text(self):
        text = self.encode_text.get('1.0', tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Успіх", "Текст скопійовано в буфер обміну.")
        else:
            messagebox.showwarning("Попередження", "Немає тексту для копіювання.")

    def clear_encode_text(self):
        self.encode_text.delete('1.0', tk.END)
        self.encode_image_label.config(image='')
        self.photo = None
        self.encode_size = None  # Скидаємо збережений розмір файлу
        self.convert_btn.config(state="disabled")
        self.compress_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")  # Деактивуємо кнопку Копіювати текст
        messagebox.showinfo("Інформація", "Вміст очищено.")

    def decode_action(self):
        encoded_str = self.decode_text.get('1.0', tk.END).strip()
        if not encoded_str:
            messagebox.showwarning("Попередження", "Введіть Base64 текст для декодування.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("GIF", "*.gif"), ("BMP", "*.bmp")],
            title="Зберегти зображення як"
        )
        if file_path:
            success = decode_image(encoded_str, file_path)
            if success:
                messagebox.showinfo("Успіх", f"Зображення збережено за адресою:\n{file_path}")
                try:
                    img = Image.open(file_path)
                    img.thumbnail((200, 200))
                    self.decoded_photo = ImageTk.PhotoImage(img)
                    img_window = tk.Toplevel(self)
                    img_window.title("Декодоване Зображення")
                    img_label = ttk.Label(img_window, image=self.decoded_photo)
                    img_label.pack(padx=10, pady=10)
                except Exception as e:
                    messagebox.showerror("Помилка", f"Не вдалося відобразити зображення:\n{e}")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
           
