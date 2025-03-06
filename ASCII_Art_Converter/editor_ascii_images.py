import cv2
from PIL import Image, ImageEnhance, ImageTk, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog, Text, Scrollbar
import os
import numpy as np

# Funzioni di elaborazione

def adjust_image(image, saturation=1.0, contrast=1.0, brightness=1.0, invert=False):
    """Applica le regolazioni all'immagine."""
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(saturation)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
    
    if invert:
        image = Image.eval(image, lambda x: 255 - x)  # Inverte ogni pixel
    
    return image

def process_image(image, output_width=200):
    """Converte l'immagine in ASCII."""
    img_gray = image.convert("L")
    width, height = img_gray.size
    aspect_ratio = height / width
    output_height = int(output_width * aspect_ratio * 0.5)
    img_gray = img_gray.resize((output_width, output_height))
    
    ascii_chars = " .:-=+*#%@"
    pixels = list(img_gray.getdata())
    ascii_image = ''.join(ascii_chars[pixel * (len(ascii_chars) - 1) // 255] for pixel in pixels)
    ascii_image = '\n'.join([ascii_image[i:i + output_width] for i in range(0, len(ascii_image), output_width)])
    
    return ascii_image

def downscale_image(image, max_width=800, max_height=600):
    """Ridimensiona l'immagine se supera le dimensioni massime."""
    width, height = image.size
    if width > max_width or height > max_height:
        aspect_ratio = height / width
        if width > max_width:
            width = max_width
            height = int(width * aspect_ratio)
        if height > max_height:
            height = max_height
            width = int(height / aspect_ratio)
        image = image.resize((width, height))
    return image

def update_preview(*args):
    """Aggiorna la preview in tempo reale."""
    if original_image:
        adjusted = adjust_image(original_image, saturation=sat_var.get(), contrast=con_var.get(), brightness=bright_var.get(), invert=inv_var.get())
        adjusted = downscale_image(adjusted)  # Downscale dell'immagine se necessario
        img_tk = ImageTk.PhotoImage(adjusted)
        preview_label.config(image=img_tk)
        preview_label.image = img_tk
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, process_image(adjusted))

def open_image():
    """Apre un'immagine."""
    global original_image
    file_path = filedialog.askopenfilename()
    if file_path:
        img = Image.open(file_path).convert("RGB")
        original_image = img
        update_preview()

def save_ascii_as_html():
    """Salva l'ASCII come file HTML."""
    file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
    if file_path:
        ascii_text = text_widget.get(1.0, tk.END)
        
        # Costruisci il contenuto HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ASCII Art</title>
            <style>
                body {{
                    font-family: "Courier New", Courier, monospace;
                    background-color: black;
                    color: white;
                    white-space: pre;
                    margin: 0;
                    padding: 20px;
                }}
            </style>
        </head>
        <body>
            <pre>{ascii_text}</pre>
        </body>
        </html>
        """

        # Salva il contenuto HTML nel file
        with open(file_path, "w") as f:
            f.write(html_content)

def copy_ascii():
    """Copia l'ASCII negli appunti."""
    root.clipboard_clear()
    root.clipboard_append(text_widget.get(1.0, tk.END))
    root.update()

# GUI
root = tk.Tk()
root.title("ASCII Art Editor")

sat_var = tk.DoubleVar(value=1.0)
con_var = tk.DoubleVar(value=1.0)
bright_var = tk.DoubleVar(value=1.0)
inv_var = tk.BooleanVar(value=False)
original_image = None

# Canvas principale per contenere tutto
canvas = tk.Canvas(root)
scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

# Bind per aggiornare la scroll region ogni volta che il contenuto cambia
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

# Aggiungi la finestra di scroll al canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Label per la preview dell'immagine
preview_label = tk.Label(scrollable_frame)
preview_label.pack()

# Scales e Checkbutton per il controllo dell'immagine
tk.Scale(scrollable_frame, label="Saturazione", from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, variable=sat_var, command=update_preview).pack()
tk.Scale(scrollable_frame, label="Contrasto", from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, variable=con_var, command=update_preview).pack()
tk.Scale(scrollable_frame, label="Luminosità", from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, variable=bright_var, command=update_preview).pack()
tk.Checkbutton(scrollable_frame, text="Inverti Colori", variable=inv_var, command=update_preview).pack()

# Bottoni per caricare, copiare e salvare l'arte ASCII
tk.Button(scrollable_frame, text="Apri Immagine", command=open_image).pack()
tk.Button(scrollable_frame, text="Copia ASCII", command=copy_ascii).pack()
tk.Button(scrollable_frame, text="Salva ASCII come HTML", command=save_ascii_as_html).pack()

# Widget di testo per visualizzare l'arte ASCII
text_widget = Text(scrollable_frame, wrap=tk.NONE, font=("Courier", 10))
text_widget.pack()

root.mainloop()
