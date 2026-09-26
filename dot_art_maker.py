import turtle
from PIL import Image

WIDTH = 700
HEIGHT = 700
STEP = 5
DOT_SIZE = 3
THRESHOLD = 100

DRAW_TIME = 5


def draw_image(image_path):
    try:
        image = Image.open(image_path).convert("L")
        image.thumbnail((WIDTH // STEP, HEIGHT // STEP))

    except FileNotFoundError:
        print("\nError: File not found!")
        return

    except Exception as e:
        print(f"\nError: Could not open the image.")
        print(f"Details: {e}")
        return

    screen = turtle.Screen()
    screen.setup(WIDTH, HEIGHT)
    screen.bgcolor("black")
    screen.title("Turtle Dot Art Maker")
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
            print("\nDrawing completed!")
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

        screen.ontimer(
            lambda: draw_row(y + 1),
            row_delay
        )

    draw_row(0)
    screen.mainloop()


def main():
    print("==============================")
    print("     TURTLE DOT ART MAKER")
    print("==============================")
    print()

    while True:
        image_path = input('Enter image path (inside ""): ').strip()

        image_path = image_path.strip('"')

        if not image_path:
            print("Error: Please enter an image path.\n")
            continue

        try:
            draw_image(image_path)
            break

        except KeyboardInterrupt:
            print("\nDrawing cancelled.")
            break

        except Exception as e:
            print(f"\nUnexpected error: {e}")
            break


if __name__ == "__main__":
    main()