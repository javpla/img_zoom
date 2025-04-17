# Main script for image zoom animation

import cv2
import numpy as np
import argparse
import sys # Import sys for exit

DEFAULT_DURATION = 5 # seconds
DEFAULT_FPS = 30
# Start transition later to make the max zoom more visible
TRANSITION_START_FACTOR = 0.9 # Start transition when 90% of zoom is complete
# Target ~30px on the shorter axis of the original image
FINAL_TARGET_SHORT_AXIS_PX = 30

# Removed detect_screen function as it's no longer used

def main():
    parser = argparse.ArgumentParser(description='Create a zoom animation between two images.')
    parser.add_argument('image1_path', help='Path to the first image (containing the screen)')
    parser.add_argument('image2_path', help='Path to the second image (the final scene)')
    parser.add_argument('-o', '--output', default='output_animation.mp4', help='Path for the output video file')
    parser.add_argument('--duration', type=float, default=DEFAULT_DURATION, help=f'Duration of the animation in seconds (default: {DEFAULT_DURATION})')
    parser.add_argument('--fps', type=int, default=DEFAULT_FPS, help=f'Frames per second for the output video (default: {DEFAULT_FPS})')
    parser.add_argument('--target_x', type=float, default=0.0, help='Horizontal offset (pixels) from the center for the zoom target (default: 0.0)')
    parser.add_argument('--target_y', type=float, default=0.0, help='Vertical offset (pixels) from the center for the zoom target (default: 0.0)')
    # Removed --initial_zoom argument
    # Removed --final_zoom and --target_fraction_size arguments
    # TODO: Add arguments for specifying screen corners manually (if needed in the future)
    args = parser.parse_args()

    print(f"Loading image 1 from: {args.image1_path}")
    img1 = cv2.imread(args.image1_path)
    if img1 is None:
        print(f"Error: Could not load image 1 from {args.image1_path}", file=sys.stderr)
        sys.exit(1)
    # Extract dimensions early
    h, w = img1.shape[:2]

    print(f"Loading image 2 from: {args.image2_path}")
    img2 = cv2.imread(args.image2_path)
    if img2 is None:
        print(f"Error: Could not load image 2 from {args.image2_path}", file=sys.stderr)
        sys.exit(1)

    # Removed call to detect_screen

    # --- Calculate Target Zoom Corners based on FINAL_TARGET_SHORT_AXIS_PX and target offsets ---
    # Calculate the base center of the image
    base_center_x = w / 2.0
    base_center_y = h / 2.0

    # Apply user-defined offsets to get the target center
    target_center_x = base_center_x + args.target_x
    target_center_y = base_center_y + args.target_y
    print(f"Base center: ({base_center_x:.1f}, {base_center_y:.1f})")
    print(f"Target offset: (x={args.target_x}, y={args.target_y})")
    print(f"Final target center: ({target_center_x:.1f}, {target_center_y:.1f})")

    # Calculate the aspect ratio
    aspect_ratio = w / h # width / height

    # Determine the target dimensions while maintaining aspect ratio,
    # ensuring the *shorter* dimension effectively matches FINAL_TARGET_SHORT_AXIS_PX.
    if w < h: # Width is shorter
        final_zoomed_w = FINAL_TARGET_SHORT_AXIS_PX
        final_zoomed_h = FINAL_TARGET_SHORT_AXIS_PX / aspect_ratio
    else: # Height is shorter or equal
        final_zoomed_h = FINAL_TARGET_SHORT_AXIS_PX
        final_zoomed_w = FINAL_TARGET_SHORT_AXIS_PX * aspect_ratio

    half_fzw = final_zoomed_w / 2.0
    half_fzh = final_zoomed_h / 2.0

    print(f"Targeting a central area corresponding to roughly {FINAL_TARGET_SHORT_AXIS_PX} pixels on the shorter axis.")
    print(f"Final view corresponds to a {final_zoomed_w:.1f}x{final_zoomed_h:.1f} pixel area in the original image, centered at ({target_center_x:.1f}, {target_center_y:.1f}).")

    # Calculate the corners of the final zoomed area centered on the *target* center
    final_zoom_corners = np.array([
        [target_center_x - half_fzw, target_center_y - half_fzh], # Top-left
        [target_center_x + half_fzw, target_center_y - half_fzh], # Top-right
        [target_center_x + half_fzw, target_center_y + half_fzh], # Bottom-right
        [target_center_x - half_fzw, target_center_y + half_fzh]  # Bottom-left
    ], dtype=np.float32)
    print(f"Target corners for zoom:\n{final_zoom_corners}")


    # --- Animation Setup ---
    # h, w = img1.shape[:2] # Moved earlier
    output_h, output_w = h, w # Use img1 dimensions for output
    num_frames = int(args.duration * args.fps)

    # Define the corners of the full image 1 (used if initial_zoom is 1.0)
    full_img1_corners = np.array([
        [0, 0],         # Top-left
        [w - 1, 0],     # Top-right
        [w - 1, h - 1], # Bottom-right
        [0, h - 1]      # Bottom-left
    ], dtype=np.float32)

    # Calculate the initial source corners based on the zoom factor
    # Always start from the full image corners
    start_corners = full_img1_corners
    print("Starting animation from full image view.")

    output_corners = np.array([
        [0, 0],
        [output_w - 1, 0],
        [output_w - 1, output_h - 1],
        [0, output_h - 1]
    ], dtype=np.float32)

    # Resize image 2 to match output dimensions
    img2_resized = cv2.resize(img2, (output_w, output_h))

    # --- Video Writer Setup ---
    # Use 'mp4v' codec for MP4 files. Others like 'XVID' for AVI might also work.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(args.output, fourcc, args.fps, (output_w, output_h))

    if not video_writer.isOpened():
        print(f"Error: Could not open video writer for path {args.output}", file=sys.stderr)
        # Clean up loaded images if necessary (though Python's GC usually handles it)
        sys.exit(1)

    print(f"Generating {num_frames} frames for {args.duration}s animation at {args.fps} FPS...")

    # --- Frame Generation Loop ---
    for i in range(num_frames):
        t = i / (num_frames - 1) # Interpolation factor (0.0 to 1.0)

        # 1. Calculate Intermediate Source Corners for the Warp
        # Interpolate from the calculated start_corners to the final_zoom_corners.
        interp_src_corners = (1 - t) * start_corners + t * final_zoom_corners

        # 2. Calculate Perspective Transform
        # This matrix maps the interp_src_corners onto the full output_corners.
        M = cv2.getPerspectiveTransform(interp_src_corners, output_corners)

        # 3. Warp Image 1
        warped_img1 = cv2.warpPerspective(img1, M, (output_w, output_h))

        # 4. Handle Transition/Crossfade
        output_frame = warped_img1
        if t >= TRANSITION_START_FACTOR:
            # Calculate alpha for crossfade (0.0 to 1.0 within the transition period)
            transition_t = (t - TRANSITION_START_FACTOR) / (1.0 - TRANSITION_START_FACTOR)
            alpha = max(0.0, min(1.0, transition_t)) # Clamp alpha between 0 and 1

            # Blend warped_img1 and img2_resized
            output_frame = cv2.addWeighted(warped_img1, 1 - alpha, img2_resized, alpha, 0)

        # 5. Write Frame to Video
        video_writer.write(output_frame)

        # Optional: Print progress
        if (i + 1) % args.fps == 0:
            print(f"Generated frame {i + 1}/{num_frames} ({(i+1)/args.fps:.1f}s)")

    # --- Cleanup ---
    video_writer.release()
    print(f"Animation saved successfully to {args.output}")

if __name__ == "__main__":
    main()
