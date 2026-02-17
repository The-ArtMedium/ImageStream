"""
Generate basic icons for LocalEdit using PIL/Pillow.
Run this script to create placeholder icons until custom ones are made.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(filename, symbol, color, size=48):
    """Create a simple icon with a symbol.
    
    Args:
        filename: Output filename
        symbol: Text symbol to draw
        color: RGB color tuple
        size: Icon size in pixels
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.6))
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), symbol, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]
    
    draw.text((x, y), symbol, fill=color, font=font)
    
    img.save(filename, 'PNG')
    print(f"Created: {filename}")

def main():
    """Generate all required icons."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    icons = [
        ('video.png', '📹', (66, 133, 244)),
        ('image.png', '🖼️', (52, 168, 83)),
        ('text.png', '📝', (251, 188, 5)),
        ('audio.png', '🎵', (234, 67, 53)),
        ('export.png', '💾', (102, 187, 106)),
        ('play.png', '▶️', (76, 175, 80)),
        ('pause.png', '⏸️', (255, 152, 0)),
        ('stop.png', '⏹️', (244, 67, 54)),
    ]
    
    print("Generating LocalEdit icons...")
    print()
    
    for filename, symbol, color in icons:
        filepath = os.path.join(script_dir, filename)
        create_icon(filepath, symbol, color)
    
    print()
    print("Icon generation complete!")
    print(f"Icons saved to: {script_dir}")

if __name__ == '__main__':
    main()
