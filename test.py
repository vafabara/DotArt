from unittest.mock import MagicMock, patch

import pytest
from PIL import Image, ImageDraw

import dot_art_maker_gui as app


def make_image(pixels, size):
    """Build a small grayscale image from a flat list of pixel values."""
    image = Image.new("L", size)
    image.putdata(pixels)
    return image


# ---------- compute_row_dots ----------

def test_bright_pixels_become_dots_with_centered_coordinates():
    # row 0: [dark, bright]   row 1: [bright, dark]
    image = make_image([0, 255, 255, 0], (2, 2))

    # spacing 4 -> start_x = -4, start_y = 4
    assert app.compute_row_dots(image, 0, 4) == [(0, 4)]
    assert app.compute_row_dots(image, 1, 4) == [(-4, 0)]


def test_all_black_row_has_no_dots():
    image = make_image([0, 0, 0], (3, 1))
    assert app.compute_row_dots(image, 0, 4) == []


def test_threshold_boundary():
    # exactly THRESHOLD is drawn, THRESHOLD - 1 is skipped
    image = make_image([app.THRESHOLD - 1, app.THRESHOLD], (2, 1))
    assert len(app.compute_row_dots(image, 0, 4)) == 1


def test_spacing_scales_positions():
    image = make_image([255, 255], (2, 1))
    near = app.compute_row_dots(image, 0, 4)
    far = app.compute_row_dots(image, 0, 7)

    assert near[1][0] - near[0][0] == 4
    assert far[1][0] - far[0][0] == 7


# ---------- screen_to_pixel ----------

def test_center_maps_to_image_center():
    assert app.screen_to_pixel(0, 0) == (app.WIDTH / 2, app.HEIGHT / 2)


def test_top_left_corner_maps_to_origin():
    assert app.screen_to_pixel(-app.WIDTH / 2, app.HEIGHT / 2) == (0, 0)


# ---------- draw_dot_on_art ----------

def test_draw_dot_on_art_paints_white_at_center_only():
    art = Image.new("RGB", (app.WIDTH, app.HEIGHT), "black")
    art_draw = ImageDraw.Draw(art)

    app.draw_dot_on_art(art_draw, 0, 0, 6)

    assert art.getpixel((app.WIDTH // 2, app.HEIGHT // 2)) == (255, 255, 255)
    assert art.getpixel((0, 0)) == (0, 0, 0)


# ---------- compute_row_delay ----------

def test_row_delay_spreads_draw_time_over_rows():
    assert app.compute_row_delay(100) == int(app.DRAW_TIME * 1000 / 100)


def test_row_delay_is_never_below_one_ms():
    assert app.compute_row_delay(10_000_000) == 1


# ---------- load_grayscale (uses real files via tmp_path) ----------

def test_load_grayscale_converts_and_shrinks(tmp_path):
    path = tmp_path / "big.png"
    Image.new("RGB", (1000, 500), "red").save(path)

    image = app.load_grayscale(str(path), 4)

    assert image.mode == "L"
    assert image.width <= app.WIDTH // 4
    assert image.height <= app.HEIGHT // 4


def test_load_grayscale_raises_for_non_image(tmp_path):
    path = tmp_path / "fake.png"
    path.write_text("this is not an image")

    with pytest.raises(Exception):
        app.load_grayscale(str(path), 4)


# ---------- save_art (GUI dialogs are mocked) ----------

@patch("dot_art_maker_gui.messagebox")
@patch("dot_art_maker_gui.filedialog.asksaveasfilename", return_value="")
def test_save_art_cancelled_does_nothing(mock_dialog, mock_box):
    art = MagicMock()
    app.save_art(art)

    art.save.assert_not_called()
    mock_box.showinfo.assert_not_called()


@patch("dot_art_maker_gui.messagebox")
@patch("dot_art_maker_gui.filedialog.asksaveasfilename", return_value="out.png")
def test_save_art_success(mock_dialog, mock_box):
    art = MagicMock()
    app.save_art(art)

    art.save.assert_called_once_with("out.png")
    mock_box.showinfo.assert_called_once()


@patch("dot_art_maker_gui.messagebox")
@patch("dot_art_maker_gui.filedialog.asksaveasfilename", return_value="out.png")
def test_save_art_failure_shows_error(mock_dialog, mock_box):
    art = MagicMock()
    art.save.side_effect = OSError

    app.save_art(art)

    mock_box.showerror.assert_called_once()
