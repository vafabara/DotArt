import tkinter as tk
from tkinter import filedialog, messagebox
import turtle
from PIL import Image, ImageDraw


WIDTH = 700
HEIGHT = 700
STEP = 5
DOT_SPACING_OPTIONS = {"NEAR": 4, "FAR": 7}
THRESHOLD = 100
DRAW_TIME = 5


# ---------------------------------------------------------------------------
# Pure logic (no GUI) - these functions are easy to unit test
# ---------------------------------------------------------------------------

def load_grayscale(image_path, dot_spacing):
    """Open an image, convert it to grayscale and shrink it so that
    one pixel = one dot fits inside the canvas."""
    image = Image.open(image_path).convert("L")
    image.thumbnail((WIDTH // dot_spacing, HEIGHT // dot_spacing))
    return image


def compute_row_dots(image, y, dot_spacing, threshold=THRESHOLD):
    """Return turtle (x, y) coordinates of every dot to draw in row y.
    Pixels darker than the threshold are skipped."""
    image_width, image_height = image.size
    start_x = -(image_width * dot_spacing) / 2
    start_y = (image_height * dot_spacing) / 2

    dots = []
    for x in range(image_width):
        if image.getpixel((x, y)) < threshold:
            continue
        dots.append((start_x + x * dot_spacing, start_y - y * dot_spacing))
    return dots


def screen_to_pixel(screen_x, screen_y):
    """Convert turtle coordinates (origin at center, y up) to
    PIL coordinates (origin at top-left, y down)."""
    return WIDTH / 2 + screen_x, HEIGHT / 2 - screen_y


def draw_dot_on_art(art_draw, screen_x, screen_y, dot_size):
    """Draw one white dot on the PIL image used for saving."""
    radius = dot_size / 2
    px, py = screen_to_pixel(screen_x, screen_y)
    art_draw.ellipse(
        (px - radius, py - radius, px + radius, py + radius),
        fill="white"
    )


def compute_row_delay(image_height):
    """Milliseconds to wait between rows so the whole drawing
    takes about DRAW_TIME seconds."""
    return max(1, int((DRAW_TIME * 1000) / image_height))


# ---------------------------------------------------------------------------
# GUI code
# ---------------------------------------------------------------------------

def save_art(art_image):
    save_path = filedialog.asksaveasfilename(
        title="Save Dot Art",
        defaultextension=".png",
        initialfile="dot_art.png",
        filetypes=[
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg *.jpeg"),
            ("BMP Image", "*.bmp")
        ]
    )

    if not save_path:
        return

    try:
        art_image.save(save_path)
        messagebox.showinfo(
            "Dot Art Maker",
            f"Saved to:\n{save_path}"
        )
    except Exception:
        messagebox.showerror(
            "Dot Art Maker",
            "Could not save the image."
        )


def draw_image(image_path, root, save_enabled, dot_size, dot_spacing):
    try:
        image = load_grayscale(image_path, dot_spacing)
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

    art_image = Image.new("RGB", (WIDTH, HEIGHT), "black")
    art_draw = ImageDraw.Draw(art_image)

    image_height = image.size[1]
    row_delay = compute_row_delay(image_height)

    def draw_row(y):
        if y >= image_height:
            screen.update()

            if save_enabled:
                save_art(art_image)

            return

        for screen_x, screen_y in compute_row_dots(image, y, dot_spacing):
            pen.goto(screen_x, screen_y)
            pen.dot(dot_size, "white")
            draw_dot_on_art(art_draw, screen_x, screen_y, dot_size)

        screen.update()
        screen.ontimer(lambda: draw_row(y + 1), row_delay)

    draw_row(0)


def select_image(root, save_var, dot_size_var, spacing_var):
    image_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All Files", "*.*")
        ]
    )

    if image_path:
        draw_image(
            image_path,
            root,
            save_var.get(),
            dot_size_var.get(),
            DOT_SPACING_OPTIONS[spacing_var.get()]
        )


def main():
    root = tk.Tk()
    root.title("Dot Art Maker")
    root.geometry("650x540")
    root.resizable(False, False)
    root.configure(bg="black")

    title_font = ("Courier New", 24, "bold")
    text_font = ("Courier New", 11)
    button_font = ("Courier New", 12, "bold")

    save_var = tk.BooleanVar(value=False)
    dot_size_var = tk.IntVar(value=3)
    spacing_var = tk.StringVar(value="NEAR")

    title = tk.Label(
        root,
        text="WELCOME TO DOT ART MAKER",
        bg="black",
        fg="white",
        font=title_font
    )
    title.pack(pady=(28, 12))

    description = tk.Label(
        root,
        text=(
            "Upload an image and turn it into dot art.\n"
            "Choose dot size and spacing, then create your artwork."
        ),
        bg="black",
        fg="white",
        font=text_font,
        justify="center"
    )
    description.pack(pady=(0, 14))

    size_label = tk.Label(
        root,
        text="CHOOSE DOT SIZE",
        bg="black",
        fg="white",
        font=("Courier New", 11, "bold")
    )
    size_label.pack(pady=(0, 8))

    size_frame = tk.Frame(root, bg="black")
    size_frame.pack(pady=(0, 12))

    sizes = [
        ("SMALL", 2),
        ("MEDIUM", 3),
        ("LARGE", 5)
    ]

    for label, size in sizes:
        tk.Radiobutton(
            size_frame,
            text=label,
            variable=dot_size_var,
            value=size,
            bg="black",
            fg="white",
            selectcolor="#3E4A2C",
            activebackground="black",
            activeforeground="white",
            font=text_font,
            cursor="hand2"
        ).pack(side="left", padx=12)

    spacing_label = tk.Label(
        root,
        text="CHOOSE DOT SPACING",
        bg="black",
        fg="white",
        font=("Courier New", 11, "bold")
    )
    spacing_label.pack(pady=(0, 8))

    spacing_frame = tk.Frame(root, bg="black")
    spacing_frame.pack(pady=(0, 12))

    for label, value in [("NEAR", "NEAR"), ("FAR", "FAR")]:
        tk.Radiobutton(
            spacing_frame,
            text=label,
            variable=spacing_var,
            value=value,
            bg="black",
            fg="white",
            selectcolor="#3E4A2C",
            activebackground="black",
            activeforeground="white",
            font=text_font,
            cursor="hand2"
        ).pack(side="left", padx=18)

    save_check = tk.Checkbutton(
        root,
        text="Save result after drawing",
        variable=save_var,
        bg="black",
        fg="white",
        selectcolor="black",
        activebackground="black",
        activeforeground="white",
        font=text_font,
        cursor="hand2"
    )
    save_check.pack(pady=(0, 12))

    select_button = tk.Button(
        root,
        text="◎  SELECT IMAGE",
        command=lambda: select_image(
            root, save_var, dot_size_var, spacing_var
        ),
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
