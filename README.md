# Image Zoom Animator

> **Note:** This script was entirely made using ChatGPT's chat agent mode in VSCode as my first attempt of "vibe coding".

This Python script creates a video animation that starts with a view of a first image, zooms into a specific target point within that image, and then transitions (crossfades) to a second image.

## Requirements

*   Python 3.x
*   OpenCV (`opencv-python`)
*   NumPy (`numpy`)

You can install the required libraries using pip:
```bash
pip install -r requirements.txt
```
*(Note: You might need to create a `requirements.txt` file containing `opencv-python` and `numpy` if you don't have one).*

## Usage

```bash
python zoom_animator.py <image1_path> <image2_path> [options]
```

**Positional Arguments:**

*   `<image1_path>`: Path to the first image (the one that will be zoomed into).
*   `<image2_path>`: Path to the second image (the final scene after the transition).

**Optional Arguments:**

*   `-o OUTPUT, --output OUTPUT`: Path for the output video file (default: `output_animation.mp4`).
*   `--duration DURATION`: Duration of the animation in seconds (default: 5.0).
*   `--fps FPS`: Frames per second for the output video (default: 30).
*   `--target_x TARGET_X`: Horizontal offset (in pixels) from the center for the zoom target. Positive values move right, negative values move left (default: 0.0).
*   `--target_y TARGET_Y`: Vertical offset (in pixels) from the center for the zoom target. Positive values move down, negative values move up (default: 0.0).

## Functionality Details

*   **Zoom Target:** The script zooms into a small area of the first image. The size of this final zoomed area is hardcoded to be approximately 30 pixels along the shorter axis of the original image, maintaining the aspect ratio.
*   **Zoom Center:** By default, the zoom targets the exact center of the first image. The `--target_x` and `--target_y` arguments allow you to shift this target point.
*   **Transition:** The animation smoothly zooms from the full view of the first image to the target area. Near the end of the zoom (specifically, after 90% of the animation duration), it starts a crossfade transition to the second image.
*   **Output:** The result is an MP4 video file.

## Example

To create an 8-second animation zooming into the center of `photo1.jpg` and transitioning to `photo2.jpg`:

```bash
python zoom_animator.py photo1.jpg photo2.jpg -o center_zoom.mp4
```

To create a 10-second animation zooming into a point 100 pixels below the center of `start_image.png` and transitioning to `end_image.png`:

```bash
python zoom_animator.py start_image.png end_image.png --duration 10 --target_y 100 -o below_center_zoom.mp4
```
