import pygame
import sys
import random
import numpy as np
import time
import csv
import pandas as pd

class FlappyBirdGame:
    def __init__(self, mode):
        pygame.init()
        self.mode = mode
        self.screen = pygame.display.set_mode((400, 708))
        pygame.display.set_caption("Flappy Bird EMG")

        # پرنده و گرافیک
        self.bird = pygame.Rect(65, 50, 50, 50)
        self.background = pygame.image.load("FlappyBird/assets/background.png").convert()
        self.birdSprites = [
            pygame.image.load("FlappyBird/assets/1.png").convert_alpha(),
            pygame.image.load("FlappyBird/assets/2.png").convert_alpha(),
            pygame.image.load("FlappyBird/assets/dead.png")
        ]
        self.wallUp = pygame.image.load("FlappyBird/assets/bottom.png").convert_alpha()
        self.wallDown = pygame.image.load("FlappyBird/assets/top.png").convert_alpha()

        # وضعیت بازی
        self.gap = 130
        self.wallx = 400
        self.birdY = 350
        self.sprite = 0
        self.counter = 0
        self.offset = random.randint(-110, 110)
        self.frame_count = 0
        self.dead = False
        self.running = True  # برای کنترل حلقه بازی

        # متغیرهای کنترلی برای حالت‌های Speed و Force
        self.NOISE_THRESHOLD = 0.005
        self.MAX_MOVE = 25
        self.MIN_MOVE = 1
        self.FORCE_SPEED = 6
        self.force_direction = 0
        self.previous_v = 0.0  # برای ذخیره v قبلی در Speed Mode (دیگه استفاده نمی‌شه)

        # فونت
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 50)

        # ساعت
        self.clock = pygame.time.Clock()

    @staticmethod
    def show_menu(screen, font):
        screen.fill((0, 0, 0))
        title = font.render("Select Game Mode", True, (255, 255, 255))
        option1 = font.render("1 - Speed Mode", True, (255, 255, 255))
        option2 = font.render("2 - Force Mode", True, (255, 255, 255))
        screen.blit(title, (50, 200))
        screen.blit(option1, (50, 260))
        screen.blit(option2, (50, 300))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return "speed"
                    elif event.key == pygame.K_2:
                        return "force"

    def updateWalls(self):
        self.wallx -= 2
        if self.wallx < -80:
            self.wallx = 400
            self.counter += 1
            self.offset = random.randint(-110, 110)

    def updateBird(self, a, v):
        if not self.dead:
            self.frame_count += 1
            if self.frame_count % int(60 / 30) == 0:  # هر 1/30 ثانیه
                if self.mode == "speed":
                    if abs(v) >= self.NOISE_THRESHOLD and a != 0:
                        move_distance = self.MIN_MOVE + v * (self.MAX_MOVE - self.MIN_MOVE)  # نگاشت v به [MIN_MOVE, MAX_MOVE]
                        direction = -1 if a > 0 else 1 if a < 0 else 0  # -1 = بالا، 1 = پایین
                        new_y = self.birdY + direction * move_distance
                        self.birdY = max(0, min(658, new_y))
                elif self.mode == "force":
                    if abs(v) >= self.NOISE_THRESHOLD:
                        self.force_direction = -1 if a > 0 else 1 if a < 0 else 0  # -1 = بالا، 1 = پایین
                    if self.force_direction != 0:
                        new_y = self.birdY + self.force_direction * self.FORCE_SPEED
                        self.birdY = max(0, min(658, new_y))

            self.bird[1] = self.birdY

            # برخورد با دیوارها
            upRect = pygame.Rect(self.wallx, 360 + self.gap - self.offset + 10,
                                 self.wallUp.get_width() - 10, self.wallUp.get_height())
            downRect = pygame.Rect(self.wallx, 0 - self.gap - self.offset - 10,
                                   self.wallDown.get_width() - 10, self.wallDown.get_height())

            if upRect.colliderect(self.bird) or downRect.colliderect(self.bird):
                self.dead = True
                self.draw_game_over()
                pygame.time.delay(2000)  # مکث ۲ ثانیه‌ای
                self.running = False  # توقف حلقه بازی برای بازگشت به منو

    def draw_game_over(self):
        # نمایش پس‌زمینه برای تمیز کردن صفحه
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))

        # نمایش متن "GAME OVER"
        game_over_font = pygame.font.SysFont("Arial", 70, bold=True)
        text_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(200, 300))  # کمی بالاتر برای جا دادن امتیاز
        self.screen.blit(text_surface, text_rect)

        # نمایش امتیاز نهایی
        score_font = pygame.font.SysFont("Arial", 40, bold=True)
        score_surface = score_font.render(f"Score: {self.counter}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(200, 380))  # زیر متن Game Over
        self.screen.blit(score_surface, score_rect)

        pygame.display.update()

    def reset_game(self):
        self.bird[1] = 50
        self.birdY = 50
        self.dead = False
        self.counter = 0
        self.wallx = 400
        self.offset = random.randint(-110, 110)
        self.force_direction = 0

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.wallUp, (self.wallx, 360 + self.gap - self.offset))
        self.screen.blit(self.wallDown, (self.wallx, 0 - self.gap - self.offset))
        self.screen.blit(self.font.render(str(self.counter), -1, (255, 255, 255)), (200, 50))

        if self.dead:
            self.sprite = 2
        self.screen.blit(self.birdSprites[self.sprite], (70, self.birdY))

        if not self.dead:
            self.sprite = 0

        pygame.display.update()

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False
        pygame.quit()
        sys.exit()

# class DummyProcessor:
#     def __call__(self, EMG_data):
#         v = random.uniform(0.01, 1.0)
#         a = random.choice([-1, 0, 1])
#         return v, a, None, None

# class CSVProcessor:
#     def __init__(self, csv_path="gesture_log1.csv"):
#         self.data = pd.read_csv(csv_path)
#         self.index = 0
#         self.total = len(self.data)

#     def __call__(self, _=None):
#         if self.index < self.total:
#             row = self.data.iloc[self.index]
#             self.index += 1
#             a = float(row.get("Gesture", 0.0))
#             v = int(row.get("FluctuationPower", 0)) * 0.005
#             #print(a, v)
#             return v, a, None, None
#         else:
#             return 0.0, 0, None, None  # End of data behavior

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 708))
    font = pygame.font.SysFont("Arial", 24)
    processor = CSVProcessor()

    while True:  # حلقه اصلی برای بازگشت به منو بعد از Game Over
        mode = FlappyBirdGame.show_menu(screen, font)  # فراخوانی show_menu از کلاس
        game = FlappyBirdGame(mode)

        while game.is_running():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.stop()

            EMG = np.random.rand(100, 2)
            v, a, _, _ = processor(EMG)

            game.updateWalls()
            game.updateBird(a, v)
            game.draw()
            game.clock.tick(60)
            time.sleep(0.01)  # تأخیر برای شبیه‌سازی ورودی EMG