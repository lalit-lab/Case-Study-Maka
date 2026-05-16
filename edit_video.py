
import os
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# --- CONFIGURATION ---
INPUT_VIDEO = r"C:\Users\Asus\Downloads\Case-Study-Maka\assets\videos\clip1.mp4"
OUTPUT_VIDEO = r"C:\Users\Asus\Downloads\Case-Study-Maka\assets\videos\clip1_edited.mp4"

# Timestamps (Video time in seconds)
# IMPORTANT: If 0:47 is the ROUND TIMER, it usually means 47 seconds LEFT.
# If the round starts at 1:55, then 0:47 happens AFTER 1 minute of play.
# I have set these as relative seconds for now. 
# PLEASE ADJUST THESE to match where you want them in the video!
T_SPOTTED = 10.0   # Example: 10 seconds into the video
T_ANALYSIS = 15.0  # Example: 15 seconds into the video
T_ELIMINATED = 25.0 # Example: 25 seconds into the video

# Duration for each overlay to stay on screen
DURATION = 4.0 

def create_overlay_image(width, height, text_list, arrows=None):
    """
    Creates a transparent image with text and arrows.
    arrows: list of tuples ((start_x, start_y), (end_x, end_y))
    """
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 40)
        title_font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()
        title_font = font

    # Draw Text Boxes with background for readability
    y_offset = 50
    for i, text in enumerate(text_list):
        # Draw a semi-transparent background for text
        text_bbox = draw.textbbox((100, y_offset), text, font=font if i > 0 else title_font)
        draw.rectangle([text_bbox[0]-10, text_bbox[1]-5, text_bbox[2]+10, text_bbox[3]+5], fill=(0, 0, 0, 160))
        draw.text((100, y_offset), text, font=font if i > 0 else title_font, fill=(255, 255, 255, 255))
        y_offset += 60

    # Draw Arrows
    if arrows:
        for (start, end) in arrows:
            # Draw line
            draw.line([start, end], fill=(255, 0, 0, 255), width=8)
            
            # Draw arrowhead (triangle)
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            angle = np.arctan2(dy, dx)
            
            arrow_size = 20
            p1 = (end[0] - arrow_size * np.cos(angle - np.pi/6), 
                  end[1] - arrow_size * np.sin(angle - np.pi/6))
            p2 = (end[0] - arrow_size * np.cos(angle + np.pi/6), 
                  end[1] - arrow_size * np.sin(angle + np.pi/6))
            
            draw.polygon([end, p1, p2], fill=(255, 0, 0, 255))

    return np.array(img)

def main():
    if not os.path.exists(INPUT_VIDEO):
        print(f"Error: Could not find {INPUT_VIDEO}")
        return

    print("Loading video...")
    video = VideoFileClip(INPUT_VIDEO)
    w, h = video.size

    overlays = []

    # --- SEGMENT 1: SPOTTED (At 0:47) ---
    img1 = create_overlay_image(w, h, 
        ["STEP 1: TARGET SPOTTED", "• Opponent seen in 2v1 situation"],
        arrows=[((w//2, h//2 - 100), (w//2, h//2))] # Pointing to center roughly
    )
    clip1 = ImageClip(img1).with_start(T_SPOTTED).with_duration(3).with_position('center')
    overlays.append(clip1)

    # --- SEGMENT 2: THE MISTAKE (At 0:46) ---
    # Pointing to Ammo (Bottom Right) and Smoke (Right Side)
    img2 = create_overlay_image(w, h, 
        ["CRITICAL ERRORS AT 0:46", 
         "• LOW AMMO: Only 2 bullets (No reload!)",
         "• EXPOSED: No cover taken",
         "• MISSED OPPORTUNITY: Smoke path ignored"],
        arrows=[
            ((w - 300, h - 200), (w - 100, h - 100)), # To Ammo
            ((w - 400, h//2), (w - 200, h//2 + 50))   # To Smoke area
        ]
    )
    clip2 = ImageClip(img2).with_start(T_ANALYSIS).with_duration(5).with_position('center')
    overlays.append(clip2)

    # --- SEGMENT 3: ELIMINATED (At 0:42) ---
    img3 = create_overlay_image(w, h, 
        ["RESULT: ELIMINATED", "• Lost duel due to low ammo & poor positioning"],
    )
    clip3 = ImageClip(img3).with_start(T_ELIMINATED).with_duration(3).with_position('center')
    overlays.append(clip3)

    print("Compositing video...")
    result = CompositeVideoClip([video] + overlays)
    
    print(f"Saving to {OUTPUT_VIDEO}...")
    # Using low preset for speed, you can change to 'medium' or 'slow' for better quality
    result.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=video.fps, preset="ultrafast")

    print("Done!")

if __name__ == "__main__":
    main()
