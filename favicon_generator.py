# favicon_generator.py
# Generate favicon and icons for the Multi-LLM Platform

from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    """Create a simple favicon for the application"""
    # Create directories if they don't exist
    os.makedirs('static', exist_ok=True)
    
    # Create a 64x64 image with gradient background
    size = 64
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background (purple to blue)
    for y in range(size):
        r = int(102 + (118 - 102) * y / size)
        g = int(102 + (126 - 102) * y / size)
        b = int(241 + (162 - 241) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    
    # Draw robot emoji-like icon
    # Head
    head_color = (255, 255, 255)
    draw.ellipse([12, 12, 52, 52], fill=head_color, outline=(100, 100, 100), width=2)
    
    # Eyes
    eye_color = (102, 102, 241)
    draw.ellipse([20, 24, 28, 32], fill=eye_color)
    draw.ellipse([36, 24, 44, 32], fill=eye_color)
    
    # Mouth
    draw.arc([22, 32, 42, 44], 0, 180, fill=(100, 100, 100), width=2)
    
    # Antenna
    draw.line([32, 12, 32, 6], fill=(100, 100, 100), width=2)
    draw.ellipse([30, 4, 34, 8], fill=(102, 102, 241))
    
    # Save as ICO (favicon)
    img.save('static/favicon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
    print("✅ Favicon created: static/favicon.ico")
    
    # Save as PNG for other uses
    img.save('static/logo.png', 'PNG')
    print("✅ Logo created: static/logo.png")

def create_domain_images():
    """Create placeholder images for each domain"""
    os.makedirs('static/images', exist_ok=True)
    
    domains = {
        'healthcare': ('🏥', (239, 68, 68)),
        'agriculture': ('🌾', (34, 197, 94)),
        'coding': ('💻', (59, 130, 246)),
        'education': ('📚', (168, 85, 247)),
        'nature_medicine': ('🌿', (16, 185, 129)),
        'tamil': ('🇮🇳', (249, 115, 22))
    }
    
    size = 400
    
    for domain, (emoji, color) in domains.items():
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for y in range(size):
            intensity = 255 - int(100 * y / size)
            draw.line([(0, y), (size, y)], fill=(color[0], color[1], color[2], intensity))
        
        # Try to draw emoji text (will be simple without emoji font)
        try:
            font = ImageFont.truetype("arial.ttf", 200)
        except:
            font = ImageFont.load_default()
        
        # Draw domain name
        text = domain.replace('_', ' ').title()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((size - text_width) // 2, (size - text_height) // 2)
        draw.text(position, text, fill='white', font=font)
        
        # Save image
        img.save(f'static/images/{domain}.png', 'PNG')
        print(f"✅ Domain image created: static/images/{domain}.png")

def create_hero_image():
    """Create a hero banner image"""
    os.makedirs('static/images', exist_ok=True)
    
    width, height = 1200, 400
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background (purple to blue)
    for y in range(height):
        r = int(102 + (118 - 102) * y / height)
        g = int(102 + (126 - 102) * y / height)
        b = int(241 + (162 - 241) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw AI circuit pattern
    for i in range(0, width, 100):
        for j in range(0, height, 100):
            draw.ellipse([i-5, j-5, i+5, j+5], fill=(255, 255, 255, 128))
            if i + 100 < width:
                draw.line([i, j, i+100, j], fill=(255, 255, 255, 64), width=2)
            if j + 100 < height:
                draw.line([i, j, i, j+100], fill=(255, 255, 255, 64), width=2)
    
    # Add text
    try:
        font_large = ImageFont.truetype("arial.ttf", 80)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    title = "Multi-LLM Platform"
    subtitle = "AI-Powered Conversations"
    
    # Draw text with shadow effect
    draw.text((width//2 - 300, height//2 - 60), title, fill=(0, 0, 0, 64), font=font_large)
    draw.text((width//2 - 295, height//2 - 65), title, fill='white', font=font_large)
    
    draw.text((width//2 - 250, height//2 + 40), subtitle, fill=(0, 0, 0, 64), font=font_small)
    draw.text((width//2 - 245, height//2 + 35), subtitle, fill='white', font=font_small)
    
    img.save('static/images/hero.png', 'PNG')
    print("✅ Hero image created: static/images/hero.png")

def create_feature_icons():
    """Create simple icons for features"""
    os.makedirs('static/images/icons', exist_ok=True)
    
    icons = {
        'chat': '💬',
        'secure': '🔒',
        'fast': '⚡',
        'models': '🤖',
        'upload': '📤',
        'history': '📚'
    }
    
    size = 128
    
    for icon_name, emoji in icons.items():
        img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw circle background
        draw.ellipse([10, 10, size-10, size-10], 
                    fill=(102, 102, 241), 
                    outline=(99, 102, 241), 
                    width=3)
        
        # Draw simple shape based on icon type
        center = size // 2
        if icon_name == 'chat':
            # Speech bubble
            draw.rectangle([30, 40, 98, 80], fill='white')
            draw.polygon([(40, 80), (30, 90), (50, 80)], fill='white')
        elif icon_name == 'secure':
            # Lock shape
            draw.rectangle([45, 60, 83, 95], fill='white')
            draw.arc([50, 40, 78, 70], 0, 180, fill='white', width=5)
        elif icon_name == 'fast':
            # Lightning bolt
            draw.polygon([(70, 30), (55, 60), (68, 60), (58, 98), (80, 55), (68, 55)], fill='white')
        elif icon_name == 'models':
            # Robot head
            draw.rectangle([45, 50, 83, 88], fill='white', outline='white')
            draw.rectangle([50, 60, 58, 68], fill=(102, 102, 241))
            draw.rectangle([70, 60, 78, 68], fill=(102, 102, 241))
            draw.line([64, 45, 64, 52], fill='white', width=3)
            draw.ellipse([62, 43, 66, 47], fill='white')
        elif icon_name == 'upload':
            # Arrow up
            draw.polygon([(64, 35), (50, 55), (58, 55), (58, 88), (70, 88), (70, 55), (78, 55)], fill='white')
        elif icon_name == 'history':
            # Book
            draw.rectangle([40, 45, 88, 90], fill='white')
            draw.line([64, 45, 64, 90], fill=(102, 102, 241), width=2)
        
        img.save(f'static/images/icons/{icon_name}.png', 'PNG')
        print(f"✅ Icon created: static/images/icons/{icon_name}.png")

def main():
    print("🎨 Generating icons and images for Multi-LLM Platform...")
    print("-" * 50)
    
    create_favicon()
    create_domain_images()
    create_hero_image()
    create_feature_icons()
    
    print("-" * 50)
    print("✨ All images generated successfully!")
    print("\nGenerated files:")
    print("  - static/favicon.ico")
    print("  - static/logo.png")
    print("  - static/images/*.png (domain images)")
    print("  - static/images/hero.png")
    print("  - static/images/icons/*.png")

if __name__ == '__main__':
    main()


# Installation instructions:
"""
To use this script:

1. Install Pillow (PIL):
   pip install Pillow

2. Run the script:
   python favicon_generator.py

3. The script will create all necessary icons and images in the static folder

Note: For production, consider using professional icon design tools or services
like Figma, Canva, or hire a designer for custom icons.
"""