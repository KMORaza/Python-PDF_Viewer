import fitz
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from ttkthemes import ThemedStyle
class PDFViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        style = ThemedStyle(self)
        style.set_theme("ubuntu")
        self.title("PDF Viewer")
        self.geometry("800x600")
        self.resizable(width=False, height=False)
        self.configure(bg="black")
        self.vertical_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.horizontal_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas = tk.Canvas(self, yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.vertical_scrollbar.config(command=self.canvas.yview)
        self.horizontal_scrollbar.config(command=self.canvas.xview)
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        rockwell_font = ("Rockwell", 11)  
        menu_bar.configure(font=rockwell_font)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        file_menu.configure(bg="black", fg="white")
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.configure(bg="black", fg="white")
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Copy", menu=edit_menu)
        edit_menu.add_command(label="Copy Text", command=self.copy_text)
        edit_menu.configure(bg="black", fg="white")
        self.pdf_doc = None
        self.tk_imgs = []
        self.scale_factor = 1.0
        self.page_gap = 10  
    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.display_pdf(file_path)
    def display_pdf(self, file_path):
        if self.pdf_doc:
            self.pdf_doc.close()
        self.pdf_doc = fitz.open(file_path)
        self.canvas.delete("all")
        self.tk_imgs = []
        total_height = 0
        max_width = 0
        for page_num in range(self.pdf_doc.page_count):
            page = self.pdf_doc[page_num]
            img = page.get_pixmap(matrix=fitz.Matrix(self.scale_factor, self.scale_factor))
            img_width, img_height = img.width, img.height
            pil_img = Image.frombytes("RGB", [img.width, img.height], img.samples)
            tk_img = ImageTk.PhotoImage(pil_img)
            offset_x = (self.canvas.winfo_width() - img_width) // 2
            offset_y = total_height
            self.canvas.create_image(offset_x, offset_y, anchor=tk.NW, image=tk_img)
            total_height += img_height + self.page_gap
            self.tk_imgs.append(tk_img)
            max_width = max(max_width, img_width)
        self.canvas.config(scrollregion=(0, 0, max_width, total_height))
        self.canvas.config(width=max_width, height=self.winfo_height())
    def zoom_in(self):
        self.scale_factor *= 1.2  
        self.display_pdf(self.pdf_doc.name)
    def zoom_out(self):
        self.scale_factor /= 1.2
        self.display_pdf(self.pdf_doc.name)
    def copy_text(self):
        if not self.pdf_doc:
            return
        current_page_num = int(self.canvas.yview()[0] * self.pdf_doc.page_count)
        if 0 <= current_page_num < self.pdf_doc.page_count:
            page = self.pdf_doc[current_page_num]
            text = page.get_text("text")
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            messagebox.showinfo("Copy Text", "Text copied to clipboard.")
    def destroy(self):
        if self.pdf_doc:
            self.pdf_doc.close()
        super().destroy()
if __name__ == "__main__":
    app = PDFViewer()
    app.mainloop()
