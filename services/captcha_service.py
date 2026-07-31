import logging
import uuid
import random
import os
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps
from config.settings import (
    CAPTCHA_SIZE, CAPTCHA_GRID_SIZE, CAPTCHA_OUTPUT_DIR, CAPTCHA_IMAGE_PATH
)
from models.captcha_model import CaptchaModel

logger = logging.getLogger(__name__)


class CaptchaService:
    def __init__(self, captcha_model: CaptchaModel):
        self.model = captcha_model
        self.size = CAPTCHA_SIZE
        self.grid_size = CAPTCHA_GRID_SIZE
        self.output_dir = CAPTCHA_OUTPUT_DIR
        self.image_path = CAPTCHA_IMAGE_PATH
        self.header_height = 150
        self.header_color = (1, 127, 141)
        self.circle_radius = 17
    
    @staticmethod
    def random_color(min_value: int = 60, max_value: int = 255) -> Tuple[int, int, int]:
        return (
            random.randint(min_value, max_value),
            random.randint(min_value, max_value),
            random.randint(min_value, max_value),
        )
    
    def create_image_and_header(self) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        img = Image.new("RGB", (self.size, self.size), "white")
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, self.size, self.header_height], fill=self.header_color)
        
        try:
            header_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 40
            )
        except:
            header_font = ImageFont.load_default()
        
        def center_text(text: str, y: int):
            b = draw.textbbox((0, 0), text, font=header_font)
            w = b[2] - b[0]
            draw.text(((self.size - w) / 2, y), text, fill="white", font=header_font)
        
        center_text("Select the number assigned in the box", 35)
        center_text("where the image is placed", 85)
        
        return img, draw
    
    def draw_grid(self, draw: ImageDraw.ImageDraw, yellow: Tuple, gray: Tuple):
        """
        Draw the 4x4 grid with checkerboard pattern.
        
        Args:
            draw: ImageDraw instance
            yellow: Yellow color tuple
            gray: Gray color tuple
        """
        grid_x = 40
        grid_y = self.header_height + 40
        cell_size = self.grid_size // 4
        
        # Draw colored squares
        for r in range(4):
            for c in range(4):
                x1 = grid_x + c * cell_size
                y1 = grid_y + r * cell_size
                color = yellow if (r + c) % 2 == 0 else gray
                draw.rectangle([x1, y1, x1 + cell_size, y1 + cell_size], fill=color)
        
        # Draw grid lines
        for i in range(5):
            x = grid_x + i * cell_size
            draw.line((x, grid_y, x, grid_y + self.grid_size), fill="gray", width=3)
            y = grid_y + i * cell_size
            draw.line((grid_x, y, grid_x + self.grid_size, y), fill="gray", width=3)
    
    def draw_number_circle(
        self,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        number: int
    ):
        font_size = max(10, int(self.circle_radius * 1.15))
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                font_size
            )
        except:
            font = ImageFont.load_default()
        
        border = max(2, self.circle_radius // 8)
        draw.ellipse(
            (cx - self.circle_radius, cy - self.circle_radius,
             cx + self.circle_radius, cy + self.circle_radius),
            fill="white",
            outline="black",
            width=border,
        )
        
        text = str(number)
        b = draw.textbbox((0, 0), text, font=font)
        tw = b[2] - b[0]
        th = b[3] - b[1]
        draw.text(
            (cx - tw / 2, cy - th / 2 - 2),
            text,
            fill="black",
            font=font,
        )
    
    def draw_numbers_in_grid(self, draw: ImageDraw.ImageDraw) -> List[int]:
        grid_x = 40
        grid_y = self.header_height + 40
        cell_size = self.grid_size // 4
        
        numbers = random.sample(range(1, 101), 16)
        for idx, number in enumerate(numbers):
            r = idx // 4
            c = idx % 4
            cx = grid_x + c * cell_size + 35
            cy = grid_y + r * cell_size + 35
            self.draw_number_circle(draw, cx, cy, number)
        
        return numbers
    
    def load_and_process_image(self) -> Image.Image:
        img = Image.open(self.image_path).convert("RGBA")
        r, g, b, a = img.split()
        
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageOps.invert(rgb)
        
        img = Image.merge("RGBA", (*rgb.split(), a))
        return img
    
    def place_image(
        self,
        main_img: Image.Image,
        monkey: Image.Image,
        numbers: List[int],
        target_number: int,
        image_scale: float = 0.48
    ):
        grid_x = 40
        grid_y = self.header_height + 40
        cell_size = self.grid_size // 4
        
        idx = numbers.index(target_number)
        row = idx // 4
        col = idx % 4
        
        x1 = int(grid_x + col * cell_size)
        y1 = int(grid_y + row * cell_size)
        
        m = monkey.copy()
        target = int(cell_size * image_scale)
        w, h = m.size
        
        if w > h:
            new_w = target
            new_h = int(h * target / w)
        else:
            new_h = target
            new_w = int(w * target / h)
        
        m = m.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        px = x1 + (cell_size - new_w) // 2
        py = y1 + (cell_size - new_h) // 2
        
        main_img.paste(m, (px, py), m)
    
    def draw_footer(self, draw: ImageDraw.ImageDraw):
        grid_x = 40
        grid_y = self.header_height + 40
        footer_height = 60
        footer_y = grid_y + self.grid_size + 20
        
        draw.rectangle(
            [grid_x, footer_y, grid_x + self.grid_size, footer_y + footer_height],
            fill=self.header_color,
        )
        
        try:
            footer_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 24
            )
        except:
            footer_font = ImageFont.load_default()
        
        footer_text = "Inspired By Human Captcha"
        bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        draw.text(
            (
                grid_x + (self.grid_size - text_w) / 2,
                footer_y + (footer_height - text_h) / 2,
            ),
            footer_text,
            fill="white",
            font=footer_font,
        )
    
    def draw_telegram_logo(self, draw: ImageDraw.ImageDraw, logo_x: int, logo_y: int):
        logo_radius = 35
        draw.ellipse(
            (
                logo_x - logo_radius,
                logo_y - logo_radius,
                logo_x + logo_radius,
                logo_y + logo_radius,
            ),
            fill=(0, 136, 204),
        )
        
        plane = [
            (logo_x - 12, logo_y + 3),
            (logo_x + 18, logo_y - 12),
            (logo_x - 2, logo_y + 18),
            (logo_x - 1, logo_y + 5),
        ]
        draw.polygon(plane, fill="white")
        draw.line(
            (logo_x - 2, logo_y + 5, logo_x + 8, logo_y + 2),
            fill=(0, 136, 204),
            width=2,
        )
    
    def draw_right_panel(self, draw: ImageDraw.ImageDraw):
        """
        Draw the right side verification panel.
        
        Args:
            draw: ImageDraw instance
        """
        grid_x = 40
        grid_y = self.header_height + 40
        right_box_width = 180
        right_box_gap = 20
        
        right_box_x = grid_x + self.grid_size + right_box_gap
        right_box_y = grid_y
        
        draw.rectangle(
            (
                right_box_x,
                right_box_y,
                right_box_x + right_box_width,
                right_box_y + self.grid_size,
            ),
            fill=(255, 255, 255),
        )
        
        try:
            title_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22
            )
            user_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 26
            )
        except:
            title_font = ImageFont.load_default()
            user_font = ImageFont.load_default()
        
        logo_radius = 35
        logo_x = right_box_x + right_box_width // 2
        logo_y = right_box_y + 90
        
        self.draw_telegram_logo(draw, logo_x, logo_y)
        
        title = "Powered by"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        
        draw.text(
            (right_box_x + (right_box_width - tw) / 2, logo_y + 60),
            title,
            fill="white",
            font=title_font,
        )
        
        username = "@Owncaptcha"
        bbox = draw.textbbox((0, 0), username, font=user_font)
        tw = bbox[2] - bbox[0]
        
        draw.text(
            (right_box_x + (right_box_width - tw) / 2, logo_y + 100),
            username,
            fill="black",
            font=user_font,
        )
    
    async def generate_captcha(self) -> Tuple[str, int, List[int]]:
        try:
            captcha_id = uuid.uuid4().hex
            filename = f"{captcha_id}.png"
            filepath = os.path.join(self.output_dir, filename)
            img, draw = self.create_image_and_header()
            yellow = self.random_color()
            gray = self.random_color()
            self.draw_grid(draw, yellow, gray)
            numbers = self.draw_numbers_in_grid(draw)
            monkey = self.load_and_process_image()
            target = random.randint(1, 16)
            self.place_image(img, monkey, numbers, numbers[target - 1])
            
            self.draw_footer(draw)
            self.draw_right_panel(draw)
            
            # Save image
            img.save(filepath)
            
            # Record in database
            answer = numbers[target - 1]
            await self.model.create_captcha(captcha_id, answer, numbers)
            
            logger.info(f"Generated CAPTCHA: {captcha_id}")
            
            return captcha_id, answer, numbers
        
        except Exception as e:
            logger.error(f"Error generating CAPTCHA: {e}")
            raise
    
    async def verify_captcha(self, captcha_id: str, user_answer: int) -> Optional[bool]:
        try:
            is_correct = await self.model.verify_captcha(captcha_id, user_answer)
            if is_correct is None:
                logger.warning(f"CAPTCHA not found: {captcha_id}")
            else:
                logger.info(
                    f"CAPTCHA verification - ID: {captcha_id}, "
                    f"Correct: {is_correct}, Answer: {user_answer}"
                )
            
            return is_correct
        
        except Exception as e:
            logger.error(f"Error verifying CAPTCHA: {e}")
            raise
    
    async def get_statistics(self) -> dict:
        try:
            return await self.model.get_statistics()
        
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    async def get_recent_captchas(self, limit: int = 50) -> List[dict]:
        try:
            return await self.model.get_recent_captchas(limit=limit)

        except Exception as e:
            logger.error(f"Error getting recent CAPTCHAs: {e}")
            return []
