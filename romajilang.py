import tkinter as tk
from tkinter import ttk, filedialog
import io
import contextlib
import re

# ----------- 🧠 ロジック：RomajiLang 実行部 -----------
def run_romaji(code: str):
    lines = code.strip().split('\n')
    py_code = ""

    def translate_expr(expr):
        expr = expr.replace("tasu", "+").replace("hiku", "-")
        expr = expr.replace("kakeru", "*").replace("waru", "/")
        return expr

    def safe_concat(expr):
        parts = expr.split("tasu")
        parts = [p.strip() for p in parts]
        converted = []
        for p in parts:
            if p.startswith('"') or p.startswith("'"):
                converted.append(p)
            else:
                converted.append(f"str({p})")
        return " + ".join(converted)

    for line in lines:
        raw = line
        line = line.strip()
        if not line:
            continue

        current_indent = len(raw) - len(line)
        indent = current_indent // 4
        indent_str = "    " * indent

        if line.startswith("hanasu"):
            msg = safe_concat(translate_expr(line[len("hanasu"):].strip()))
            py_code += f"{indent_str}print({msg})\n"

        elif line.startswith("kansuu"):
            func_name = line[len("kansuu"):].strip()
            py_code += f"{indent_str}def {func_name}():\n"

        elif line.startswith("yobidasi"):
            func_name = line[len("yobidasi"):].strip()
            py_code += f"{indent_str}{func_name}()\n"

        elif "wa" in line and not line.startswith("moshi"):
            var, expr = line.split("wa", 1)
            py_code += f"{indent_str}{var.strip()} = {translate_expr(expr.strip())}\n"

        elif line.startswith("moshi"):
            match = re.match(r"moshi (.+) wa (.+) nara", line)
            if match:
                var, val = match.groups()
                py_code += f"{indent_str}if {var.strip()} == {val.strip()}:\n"

        elif line.startswith("soreigai"):
            py_code += f"{indent_str}else:\n"

        elif line.startswith("yameyo"):
            continue

        else:
            py_code += f"{indent_str}{translate_expr(line)}\n"

    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            exec(py_code, {})
        except Exception as e:
            print(f"\033[91m[エラー] {e}\033[0m")

    return output.getvalue()


# ----------- 🪟 GUI部 -----------
def create_gui():
    root = tk.Tk()
    root.title("RomajiLang IDE")
    root.geometry("850x600")

    current_theme = {"bg": "white", "fg": "black", "output_bg": "#f4f4f4", "output_fg": "black"}

    def apply_theme(theme):
        nonlocal current_theme
        current_theme = theme
        code_input.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])
        output_box.config(bg=theme["output_bg"], fg=theme["output_fg"])
        line_numbers.config(bg=theme["bg"], fg=theme["fg"])

    light_theme = {"bg": "white", "fg": "black", "output_bg": "#f4f4f4", "output_fg": "black"}
    dark_theme = {"bg": "#1e1e1e", "fg": "#dddddd", "output_bg": "#2e2e2e", "output_fg": "#ffcccc"}

    def save_file():
        path = filedialog.asksaveasfilename(defaultextension=".rmj")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code_input.get("1.0", tk.END))

    def load_file():
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                code_input.delete("1.0", tk.END)
                code_input.insert("1.0", f.read())

    def update_line_numbers(event=None):
        code = code_input.get("1.0", tk.END)
        lines = code.count('\n') + 1
        line_text = "\n".join(str(i) for i in range(1, lines + 1))
        line_numbers.config(state="normal")
        line_numbers.delete("1.0", tk.END)
        line_numbers.insert("1.0", line_text)
        line_numbers.config(state="disabled")

    def on_run():
        romaji_code = code_input.get("1.0", "end-1c")
        result = run_romaji(romaji_code)

        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)

        if "[エラー]" in result:
            output_box.insert(tk.END, result)
            output_box.tag_config("error", foreground="red")
            output_box.tag_add("error", "1.0", "end")
        else:
            output_box.insert(tk.END, result)

        output_box.config(state="disabled")

    # メニュー
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="📂 開く", command=load_file)
    file_menu.add_command(label="💾 保存", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="終了", command=root.quit)

    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="🌞 ライトモード", command=lambda: apply_theme(light_theme))
    theme_menu.add_command(label="🌙 ダークモード", command=lambda: apply_theme(dark_theme))

    menubar.add_cascade(label="ファイル", menu=file_menu)
    menubar.add_cascade(label="テーマ", menu=theme_menu)
    root.config(menu=menubar)

    # エディタ + 行番号
    editor_frame = tk.Frame(root)
    editor_frame.pack(fill="both", expand=True)

    line_numbers = tk.Text(editor_frame, width=4, padx=5, takefocus=0, border=0,
                           background="white", foreground="gray", state="disabled")
    line_numbers.pack(side="left", fill="y")

    code_input = tk.Text(editor_frame, font=("Consolas", 12), undo=True)
    code_input.pack(side="left", fill="both", expand=True)
    code_input.bind("<KeyRelease>", update_line_numbers)

    # 実行ボタン
    ttk.Button(root, text="🚀 実行", command=on_run).pack(pady=5)

    # 出力欄
    output_box = tk.Text(root, height=10, font=("Consolas", 11), state="disabled")
    output_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # 初期サンプル
    sample = """kansuu aisatu
    hanasu "Konnichiwa!"
    hanasu "RomajiLang he youkoso!"
yameyo

x wa 10
moshi x wa 10 nara
    yobidasi aisatu
soreigai
    hanasu "x wa chigau"
yameyo"""
    code_input.insert("1.0", sample)
    update_line_numbers()
    apply_theme(light_theme)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
