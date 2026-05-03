import os
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from pathlib import Path

class SaveEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Upload Labs Save Editor By podpivasss")
        self.root.geometry("700x700")
        self.root.resizable(False, False)


        self.dark_mode = False
        self.colors = self.get_colors()

        self.file_path = tk.StringVar()
        self.file_path.set(self.find_save_file())

        self.status = tk.StringVar(value="Готов")


        self.keys = [
            "corporation_data",
            "government_data",
            "money",
            "research",
            "research_advanced",
            "token",
            "code_level"
        ]
        self.vars = {key: tk.StringVar() for key in self.keys}
        self.limit_vars = {key: tk.StringVar() for key in self.keys if key != "code_level"}  # для остальных
        self.limit_enabled = tk.BooleanVar(value=False)


        self.presets_file = Path(__file__).parent / "presets.json"
        self.presets = self.load_presets()
        self.current_preset = tk.StringVar()


        self.style = ttk.Style()
        self.setup_styles()

        self.create_widgets()
        self.update_preset_list()
        self.apply_theme()

    def get_colors(self):

        if self.dark_mode:
            return {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "entry_bg": "#3c3c3c",
                "entry_fg": "#ffffff",
                "button_bg": "#3c3c3c",
                "button_fg": "#ffffff",
                "frame_bg": "#333333",
                "label_fg": "#ffffff",
                "highlight": "#1e90ff",
                "error_bg": "#8b0000"
            }
        else:
            return {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "button_bg": "#e1e1e1",
                "button_fg": "#000000",
                "frame_bg": "#d9d9d9",
                "label_fg": "#000000",
                "highlight": "#0078d7",
                "error_bg": "#ffcccc"
            }

    def setup_styles(self):

        colors = self.colors
        self.style.theme_use("clam")
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["label_fg"])
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabelframe", background=colors["bg"], foreground=colors["label_fg"])
        self.style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["label_fg"])
        self.style.configure("TButton", background=colors["button_bg"], foreground=colors["button_fg"],
                             borderwidth=1, focusthickness=3, focuscolor=colors["highlight"])
        self.style.map("TButton",
                       background=[("active", colors["highlight"]), ("pressed", colors["highlight"])])
        self.style.configure("TCombobox", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"],
                             background=colors["button_bg"], arrowcolor=colors["fg"])
        self.style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"])

    def toggle_theme(self):

        self.dark_mode = not self.dark_mode
        self.colors = self.get_colors()
        self.setup_styles()
        self.apply_theme()

    def apply_theme(self):


        self.root.configure(bg=self.colors["bg"])


        for child in self.root.winfo_children():
            self.update_widget_colors(child)


        self.theme_btn.config(text="🌙 Тёмная" if not self.dark_mode else "☀️ Светлая")


        self.root.update_idletasks()

    def update_widget_colors(self, widget):

        try:
            if isinstance(widget, tk.Entry):
                widget.configure(bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
                                 insertbackground=self.colors["fg"])
            elif isinstance(widget, tk.Label) and not isinstance(widget, ttk.Label):
                widget.configure(bg=self.colors["bg"], fg=self.colors["label_fg"])
            elif isinstance(widget, tk.Frame) and not isinstance(widget, ttk.Frame):
                widget.configure(bg=self.colors["bg"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=self.colors["entry_bg"], fg=self.colors["entry_fg"])
        except:
            pass

        for child in widget.winfo_children():
            self.update_widget_colors(child)

    def find_save_file(self):

        home = Path.home()
        candidates = [
            home / "AppData" / "Roaming" / "Upload Labs" / "savegame.dat",
            home / "Library" / "Application Support" / "Upload Labs" / "savegame.dat",
            home / ".local" / "share" / "Upload Labs" / "savegame.dat"
        ]
        for path in candidates:
            if path.exists():
                return str(path)
        return str(candidates[0])

    def create_widgets(self):

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="Файл сохранения:").pack(side="left")
        self.file_entry = ttk.Entry(top_frame, textvariable=self.file_path, width=45)
        self.file_entry.pack(side="left", padx=5)
        ttk.Button(top_frame, text="Обзор", command=self.browse_file).pack(side="left")
        ttk.Button(top_frame, text="Загрузить", command=self.load_values).pack(side="left", padx=5)


        self.theme_btn = ttk.Button(top_frame, text="🌙 Тёмная" if not self.dark_mode else "☀️ Светлая",
                                    command=self.toggle_theme)
        self.theme_btn.pack(side="right", padx=5)


        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)


        ttk.Label(main_frame, text="Переменная", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(main_frame, text="Текущее значение", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(main_frame, text="Лимит (опц.)", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=2)


        self.entries = {}
        self.limit_entries = {}
        for i, key in enumerate(self.keys, start=1):

            ttk.Label(main_frame, text=key.replace("_", " ").title() + ":", anchor="e").grid(row=i, column=0, sticky="e", padx=5, pady=2)


            entry = tk.Entry(main_frame, textvariable=self.vars[key], width=25,
                             bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
                             insertbackground=self.colors["fg"])
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.bind("<KeyRelease>", lambda e, k=key: self.validate_field(k))
            self.entries[key] = entry


            if key == "code_level":

                label = tk.Label(main_frame, text="300", width=10, anchor="w",
                                 bg=self.colors["bg"], fg=self.colors["label_fg"])
                label.grid(row=i, column=2, padx=5, pady=2)

                self.limit_label_code_level = label
            else:
                lim_entry = tk.Entry(main_frame, textvariable=self.limit_vars[key], width=10,
                                     bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
                                     insertbackground=self.colors["fg"])
                lim_entry.grid(row=i, column=2, padx=5, pady=2)
                lim_entry.bind("<KeyRelease>", lambda e, k=key: self.validate_limit_field(k))
                self.limit_entries[key] = lim_entry


        limit_frame = ttk.LabelFrame(self.root, text="Лимиты", padding=5)
        limit_frame.pack(fill="x", padx=10, pady=5)

        self.limit_check = ttk.Checkbutton(limit_frame, text="Включить проверку лимитов (кроме code_level)",
                                           variable=self.limit_enabled)
        self.limit_check.pack(anchor="w")
        ttk.Button(limit_frame, text="Установить одинаковый лимит для всех (кроме code_level)",
                   command=self.set_uniform_limit).pack(anchor="w", pady=2)


        preset_frame = ttk.LabelFrame(self.root, text="Пресеты", padding=5)
        preset_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(preset_frame, text="Выбрать пресет:").pack(side="left")
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.current_preset, width=30)
        self.preset_combo.pack(side="left", padx=5)
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_selected)

        ttk.Button(preset_frame, text="Применить", command=self.apply_preset).pack(side="left", padx=2)
        ttk.Button(preset_frame, text="Сохранить как...", command=self.save_preset).pack(side="left", padx=2)
        ttk.Button(preset_frame, text="Удалить", command=self.delete_preset).pack(side="left", padx=2)


        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Сбросить изменения", command=self.reset_values, width=20).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить", command=self.save_values, width=20).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Выход", command=self.root.quit, width=10).pack(side="right", padx=5)


        self.status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл сохранения",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.file_path.get())
        )
        if filename:
            self.file_path.set(filename)

    def validate_field(self, key):

        val = self.vars[key].get().strip()
        entry = self.entries[key]
        if val and not self.is_number(val):
            entry.config(bg=self.colors["error_bg"])
        else:
            entry.config(bg=self.colors["entry_bg"])

    def validate_limit_field(self, key):

        val = self.limit_vars[key].get().strip()
        entry = self.limit_entries[key]
        if val and not self.is_number(val):
            entry.config(bg=self.colors["error_bg"])
        else:
            entry.config(bg=self.colors["entry_bg"])

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def load_values(self):
        filepath = self.file_path.get()
        if not os.path.isfile(filepath):
            messagebox.showerror("Ошибка", "Файл не найден.")
            self.status.set("Ошибка: файл не найден")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            self.status.set("Ошибка чтения")
            return

        for key in self.keys:
            value = self.extract_value(content, key)
            if value is not None:
                self.vars[key].set(value)

                self.entries[key].config(bg=self.colors["entry_bg"])
            else:
                self.vars[key].set("")
                messagebox.showwarning("Предупреждение", f"Ключ '{key}' не найден в файле.")

        self.status.set("Значения загружены")
        messagebox.showinfo("Загрузка", "Значения загружены.")

    def extract_value(self, text, key):
        pattern = rf'"{key}":\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def reset_values(self):
        self.load_values()

    def set_uniform_limit(self):
        limit = simpledialog.askstring("Единый лимит", "Введите максимальное значение для всех переменных (кроме code_level):")
        if limit and self.is_number(limit):
            for key in self.limit_entries:
                self.limit_vars[key].set(limit)
                self.limit_entries[key].config(bg=self.colors["entry_bg"])
            self.status.set("Единый лимит установлен")
        elif limit:
            messagebox.showerror("Ошибка", "Введите корректное число.")


    def load_presets(self):
        default_preset = {
            "Базовый": {
                "corporation_data": "2.080210911784015e+60",
                "government_data": "2.080210911784015e+60",
                "money": "2.080210911784015e+60",
                "research": "2.080210911784015e+60",
                "research_advanced": "2.080210911784015e+60",
                "token": "2.080210911784015e+60",
                "code_level": "0"
            }
        }
        if self.presets_file.exists():
            try:
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
                if "Базовый" not in presets:
                    presets["Базовый"] = default_preset["Базовый"]
                return presets
            except:
                return default_preset
        else:
            return default_preset

    def save_presets_to_file(self):
        try:
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить пресеты:\n{e}")

    def update_preset_list(self):
        self.preset_combo['values'] = list(self.presets.keys())
        if self.presets:
            self.current_preset.set(list(self.presets.keys())[0])

    def on_preset_selected(self, event=None):
        pass

    def apply_preset(self):
        preset_name = self.current_preset.get()
        if not preset_name or preset_name not in self.presets:
            return
        preset = self.presets[preset_name]
        for key, value in preset.items():
            if key in self.vars:
                self.vars[key].set(value)
                self.entries[key].config(bg=self.colors["entry_bg"])
        self.status.set(f"Пресет '{preset_name}' применён")
        messagebox.showinfo("Пресет", f"Пресет '{preset_name}' применён.")

    def save_preset(self):
        name = simpledialog.askstring("Сохранить пресет", "Введите имя пресета:")
        if not name:
            return
        if name in self.presets:
            if not messagebox.askyesno("Подтверждение", f"Пресет '{name}' уже существует. Перезаписать?"):
                return

        preset_data = {}
        for key in self.keys:
            val = self.vars[key].get().strip()
            preset_data[key] = val if val else "0"

        self.presets[name] = preset_data
        self.save_presets_to_file()
        self.update_preset_list()
        self.current_preset.set(name)
        self.status.set(f"Пресет '{name}' сохранён")

    def delete_preset(self):
        name = self.current_preset.get()
        if not name or name == "Базовый":
            messagebox.showwarning("Предупреждение", "Базовый пресет нельзя удалить.")
            return
        if name not in self.presets:
            return
        if messagebox.askyesno("Удаление", f"Удалить пресет '{name}'?"):
            del self.presets[name]
            self.save_presets_to_file()
            self.update_preset_list()
            self.status.set(f"Пресет '{name}' удалён")


    def save_values(self):
        filepath = self.file_path.get()
        if not os.path.isfile(filepath):
            messagebox.showerror("Ошибка", "Файл не найден.")
            return

        for key in self.keys:
            val = self.vars[key].get().strip()
            if val and not self.is_number(val):
                messagebox.showerror("Ошибка", f"Значение {key} ('{val}') не является числом.")
                return

        cl_val = self.vars["code_level"].get().strip()
        if cl_val:
            try:
                if float(cl_val) > 300:
                    messagebox.showerror("Ошибка", f"code_level ({cl_val}) превышает лимит 300.")
                    return
            except ValueError:
                pass

        if self.limit_enabled.get():
            for key, lim_var in self.limit_vars.items():
                lim_str = lim_var.get().strip()
                if lim_str:
                    try:
                        limit = float(lim_str)
                    except ValueError:
                        messagebox.showerror("Ошибка", f"Лимит для {key} ('{lim_str}') не число.")
                        return
                    val_str = self.vars[key].get().strip()
                    if val_str:
                        val = float(val_str)
                        if val > limit:
                            messagebox.showerror("Ошибка", f"Значение {key} ({val}) превышает лимит {limit}.")
                            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            return

        for key in self.keys:
            new_val = self.vars[key].get().strip()
            if new_val:
                pattern = rf'("{key}":\s*)-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?'
                repl = rf'\g<1>{new_val}'
                content, count = re.subn(pattern, repl, content, count=1)
                if count == 0:
                    messagebox.showwarning("Предупреждение", f"Ключ '{key}' не найден. Замена не выполнена.")

        backup_path = filepath + ".bak"
        try:
            os.replace(filepath, backup_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать резервную копию:\n{e}")
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            os.replace(backup_path, filepath)
            messagebox.showerror("Ошибка", f"Не удалось записать файл:\n{e}")
            return

        self.status.set("Изменения сохранены. Резервная копия создана.")
        messagebox.showinfo("Успех", "Изменения сохранены.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditorApp(root)
    root.mainloop()