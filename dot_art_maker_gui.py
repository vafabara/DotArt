import tkinter as tk
from tkinter import filedialog, messagebox
import turtle
from PIL import Image


WIDTH = 700
HEIGHT = 700
STEP = 5
DOT_SIZE = 3
THRESHOLD = 100
DRAW_TIME = 5


def draw_image(image_path, root):
    try:
        image = Image.open(image_path).convert("L")
        image.thumbnail((WIDTH // STEP, HEIGHT // STEP))
    except Exception:
        messagebox.showerror(
            "Dot Art Maker",
            "Could not open the selected image."
        )
        return

    root.withdraw()

    screen = turtle.Screen()
    screen.setup(WIDTH, HEIGHT)
    screen.bgcolor("black")
    screen.title("Dot Art Maker")
    screen.tracer(0, 0)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.penup()
    pen.speed(0)

    image_width, image_height = image.size

    start_x = -(image_width * STEP) / 2
    start_y = (image_height * STEP) / 2

    row_delay = max(1, int((DRAW_TIME * 1000) / image_height))

    def draw_row(y):
        if y >= image_height:
            screen.update()
            return

        for x in range(image_width):
            brightness = image.getpixel((x, y))

            if brightness < THRESHOLD:
                continue

            screen_x = start_x + x * STEP
            screen_y = start_y - y * STEP

            pen.goto(screen_x, screen_y)
            pen.dot(DOT_SIZE, "white")

        screen.update()
        screen.ontimer(lambda: draw_row(y + 1), row_delay)

    draw_row(0)


def select_image(root):
    image_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All Files", "*.*")
        ]
    )

    if image_path:
        draw_image(image_path, root)


def main():
    root = tk.Tk()
    root.title("Dot Art Maker")
    root.geometry("650x400")
    root.resizable(False, False)
    root.configure(bg="black")

    title_font = ("Courier New", 24, "bold")
    text_font = ("Courier New", 11)
    button_font = ("Courier New", 12, "bold")

    title = tk.Label(
        root,
        text="WELCOME TO DOT ART MAKER",
        bg="black",
        fg="white",
        font=title_font
    )
    title.pack(pady=(75, 18))

    description = tk.Label(
        root,
        text=(
            "Upload a preferably black and white image\n"
            "and get its dot art made with Turtle."
        ),
        bg="black",
        fg="white",
        font=text_font,
        justify="center"
    )
    description.pack(pady=(0, 35))

    select_button = tk.Button(
        root,
        text="◎  SELECT IMAGE",
        command=lambda: select_image(root),
        bg="black",
        fg="white",
        activebackground="white",
        activeforeground="black",
        font=button_font,
        relief="solid",
        bd=1,
        padx=18,
        pady=10,
        cursor="hand2"
    )
    select_button.pack()

    root.mainloop()


if __name__ == "__main__":
    main()
