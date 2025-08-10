# render_manager.py

import pygame
import random
from typing import List, Tuple, Optional
from tilemap_renderer import TileMapManager
from ui_manager import UIManager
from audio_manager import audio_manager
from settings import *
from settings import resource_path

class RenderManager:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.tilemap_manager = TileMapManager()
        self.ui_manager = UIManager(screen)
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 기존 배경 이미지
        try:
            self.background_image = pygame.image.load(resource_path("assets/bg/background.png")).convert()
        except FileNotFoundError:
            self.background_image = None
            
        # 오프닝 이미지들 로드 및 랜덤 선택
        self.opening_backgrounds = []
        opening_files = [
            "AnimalBridge_opening_gray.png",
            "AnimalBridge_opening_green.png", 
            "AnimalBridge_opening_ivory.png",
            "AnimalBridge_opening_violet.png",
            "AnimalBridge_opening_yellow.png"
        ]
        
        for filename in opening_files:
            try:
                original_image = pygame.image.load(resource_path(f"assets/bg/{filename}")).convert()
                scaled_image = pygame.transform.scale(original_image, (self.width, self.height))
                self.opening_backgrounds.append(scaled_image)
                print(f"✓ 오프닝 배경 로드 성공: {filename}")
            except FileNotFoundError:
                print(f"✗ 오프닝 배경 로드 실패: {filename}")
        
        # 랜덤하게 하나 선택 (이미지가 있을 경우)
        if self.opening_backgrounds:
            self.current_opening_background = random.choice(self.opening_backgrounds)
        else:
            self.current_opening_background = None
            print("⚠️ 사용 가능한 오프닝 배경 이미지가 없습니다.")
        
        # 폰트 초기화 추가
        self.fonts = init_fonts()
        
        self.text_surface_cache = None

    def update_screen_size(self, width: int, height: int):
        self.width = width; self.height = height
        self.ui_manager.screen = self.screen
        
        # 기존 배경 이미지 스케일링
        if self.background_image:
            self.background_image = pygame.transform.scale(self.background_image, (width, height))
        
        # 오프닝 배경들 다시 스케일링
        opening_files = [
            "AnimalBridge_opening_gray.png",
            "AnimalBridge_opening_green.png", 
            "AnimalBridge_opening_ivory.png",
            "AnimalBridge_opening_violet.png",
            "AnimalBridge_opening_yellow.png"
        ]
        
        self.opening_backgrounds.clear()
        for filename in opening_files:
            try:
                original_image = pygame.image.load(resource_path(f"assets/bg/{filename}")).convert()
                scaled_image = pygame.transform.scale(original_image, (width, height))
                self.opening_backgrounds.append(scaled_image)
            except FileNotFoundError:
                pass
        
        # 현재 선택된 배경도 다시 스케일링
        if self.opening_backgrounds:
            self.current_opening_background = random.choice(self.opening_backgrounds)
        
        self.text_surface_cache = None

    def render_background(self, type: str = "default"):
        if self.background_image: 
            self.screen.blit(self.background_image, (0, 0))
        else: 
            self.screen.fill(BACKGROUND_COLOR)

    def render_terrain(self, terrain_rects: List[pygame.Rect]):
        self.tilemap_manager.terrain_renderer.render_terrain(self.screen, terrain_rects)

    def render_hazard_floor(self):
        """화면 하단에 가시 바닥을 그립니다."""
        spike_color = (60, 60, 65)
        spike_shadow_color = (40, 40, 45)
        spike_width = scale_x(30)
        spike_height = scale_y(30)
        num_spikes = self.width // spike_width + 2

        for i in range(num_spikes):
            x = i * spike_width
            base_y = self.height
            
            shadow_points = [
                (x - spike_width / 2 + 2, base_y),
                (x + spike_width / 2 + 2, base_y),
                (x + 2, base_y - spike_height)
            ]
            pygame.draw.polygon(self.screen, spike_shadow_color, shadow_points)

            points = [
                (x - spike_width / 2, base_y),
                (x + spike_width / 2, base_y),
                (x, base_y - spike_height)
            ]
            pygame.draw.polygon(self.screen, spike_color, points)

    def render_stage1_tutorial(self):
        """1스테이지 시작 시 튜토리얼 팝업을 그립니다."""
        self.ui_manager.draw_overlay((0, 0, 0, 180))
        
        panel_rect = pygame.Rect(0, 0, scale_x(800), scale_y(450))
        panel_rect.center = (self.width / 2, self.height / 2)
        self.ui_manager.draw_panel(panel_rect, (40, 40, 50, 230), WHITE, 3, 15)

        title_font = self.fonts['title_small']
        body_font = self.fonts['body_medium']
        prompt_font = self.fonts['body_small']
        
        self.ui_manager.draw_centered_text("환영합니다!", title_font, YELLOW, (panel_rect.centerx, panel_rect.top + scale_y(60)))
        
        tutorial_lines = [
            "목표: 동물 블록으로 다리를 만들어 플레이어를 깃발까지 보내주세요.",
            "조작: 하단 아이콘을 클릭해 동물을 설치할 수 있습니다.",
            "주의: 육식동물은 근처의 초식동물을 먹을 수 있어요!"
        ]
        
        for i, line in enumerate(tutorial_lines):
            y_offset = panel_rect.top + scale_y(150) + i * scale_y(50)
            self.ui_manager.draw_centered_text(line, body_font, WHITE, (panel_rect.centerx, y_offset))

        self.ui_manager.draw_centered_text("(아무 곳이나 클릭하거나 키를 누르면 시작합니다)", prompt_font, GRAY, (panel_rect.centerx, panel_rect.bottom - scale_y(50)))

    def render_start_menu(self, player_name: str, input_active: bool, input_box: pygame.Rect, next_button_rect: pygame.Rect, fonts: dict):
        # 오프닝 배경 이미지가 있으면 배경 이미지를, 없으면 흰색 배경을 그린다
        if self.current_opening_background:
            self.screen.blit(self.current_opening_background, (0, 0))
        else:
            self.screen.fill(WHITE)
        
      
        self.ui_manager.draw_text_input(input_box, player_name, fonts['input'], "클릭해서 이름을 작성하세요", fonts['placeholder'], input_active)
        self.ui_manager.draw_interactive_button(next_button_rect, "다음", fonts['prompt'], (220, 220, 220), WHITE, (100, 100, 100))

    def render_main_menu(self, player_name: str, button_rects: dict, fonts: dict):
        # 오프닝 배경 이미지가 있으면 배경 이미지를, 없으면 흰색 배경을 그린다
        if self.current_opening_background:
            self.screen.blit(self.current_opening_background, (0, 0))
        else:
            self.screen.fill(WHITE)
        
        # 배경과 상관없이 항상 실행되어야 하는 UI 요소들
        name_surf = fonts['name'].render(player_name, True, BLACK)
        name_rect = name_surf.get_rect(right=self.width - scale_x(40), top=scale_y(40))
        self.ui_manager.draw_panel(name_rect.inflate(scale_x(20), scale_y(10)), GRAY, border_color=GRAY, border_width=0, border_radius=5)
        self.screen.blit(name_surf, name_rect)
        self.ui_manager.draw_interactive_button(button_rects['start'], "게임 시작", fonts['button'], (220, 220, 220), WHITE, (100, 100, 100))
        self.ui_manager.draw_interactive_button(button_rects['desc'], "설명", fonts['button'], (220, 220, 220), WHITE, (100, 100, 100))
        self.ui_manager.draw_interactive_button(button_rects['rank'], "랭킹", fonts['button'], (220, 220, 220), WHITE, (100, 100, 100))
        
        # settings 버튼(톱니바퀴)
        self.ui_manager.draw_gear(button_rects['settings'], GRAY)

    def prepare_description_assets(self):
        fonts = {
            'title': self.fonts['title_medium'], 
            'header': self.fonts['header'], 
            'body': self.fonts['body_small'], 
            'button': self.fonts['button_small']
        }
        
        lines = [("목표", fonts['header'], YELLOW), 
                 ("동물 블록을 쌓아 다리를 만들어 플레이어가 깃발에 닿게 해주세요.", fonts['body'], WHITE), 
                 ("", fonts['body'], WHITE), 
                 ("조작 방법", fonts['header'], YELLOW), 
                 ("A / D : 플레이어 좌/우 이동", fonts['body'], WHITE), 
                 ("Space : 점프", fonts['body'], WHITE), 
                 ("마우스 클릭 : 동물 블록 선택 및 설치", fonts['body'], WHITE),
                 ("R (드래그 중) : 동물 블록 회전", fonts['body'], WHITE),
                 ("", fonts['body'], WHITE),
                 ("게임 규칙", fonts['header'], YELLOW),
                 (" - 육식동물은 근처의 초식동물을 먹을 수 있습니다.", fonts['body'], WHITE),
                 (" - 사용한 동물은 다시 사용할 수 없습니다.", fonts['body'], WHITE)]
        
        panel_rect = pygame.Rect(0, 0, scale_x(1280 - 200), scale_y(720 - 150)); panel_rect.center = (self.width / 2, self.height / 2)
        back_button_rect = pygame.Rect(0, 0, scale_x(220), scale_y(70)); back_button_rect.center = (self.width / 2, panel_rect.bottom - scale_y(60))
        
        text_area_rect = pygame.Rect(panel_rect.x + scale_x(50), panel_rect.y + scale_y(120), panel_rect.width - scale_x(120), panel_rect.height - scale_y(220))
        scroll_bar_rect = pygame.Rect(text_area_rect.right + scale_x(10), text_area_rect.y, scale_x(20), text_area_rect.height)

        self.text_surface_cache = self.ui_manager.create_text_surface(lines, scale_y(15))
        
        text_content_height = self.text_surface_cache.get_height()
        
        return lines, text_area_rect, scroll_bar_rect, back_button_rect, text_content_height
        
    def render_description_screen(self, text_surface, scroll_y, ui_elements, button_text="뒤로 가기"):
        self.render_background()
        self.ui_manager.draw_overlay((0, 0, 0, 180))
        
        panel_rect = pygame.Rect(0, 0, scale_x(1280 - 200), scale_y(720 - 150)); panel_rect.center = (self.width / 2, self.height / 2)
        
        text_area_rect = ui_elements['text_area_rect']
        scroll_bar_rect = ui_elements['scroll_bar_rect']
        back_button_rect = ui_elements['back_button_rect']
        text_content_height = ui_elements['text_content_height']

        title_font = self.fonts['title_medium']
        button_font = self.fonts['button_small']

        self.ui_manager.draw_panel(panel_rect, (40, 40, 50, 230), WHITE, 3, 15)
        title_surf = title_font.render("게임 설명", True, WHITE)
        self.screen.blit(title_surf, title_surf.get_rect(center=(panel_rect.centerx, panel_rect.top + scale_y(60))))
        
        self.ui_manager.draw_scrollable_text(text_surface, text_area_rect, scroll_y)
        self.ui_manager.draw_scroll_bar(scroll_bar_rect, text_content_height, text_area_rect.height, scroll_y)
        
        self.ui_manager.draw_interactive_button(back_button_rect, button_text, button_font, (220, 220, 220), WHITE, (100, 100, 100))

    def prepare_settings_assets(self):
        settings_bg_rect = pygame.Rect(0, 0, scale_x(1280 - 400), scale_y(720 - 400)); settings_bg_rect.center = (self.width / 2, self.height / 2)
        back_button_rect = pygame.Rect(0, 0, scale_x(220), scale_y(70)); back_button_rect.center = (self.width / 2, settings_bg_rect.bottom - scale_y(60))
        y_pos_sound = settings_bg_rect.centery
        sound_slider_rect = pygame.Rect(0, 0, scale_x(300), scale_y(15)); sound_slider_rect.midleft = (settings_bg_rect.centerx - scale_x(130), y_pos_sound)
        sound_handle_rect = pygame.Rect(0, 0, scale_x(20), scale_y(40)); sound_handle_rect.centery = sound_slider_rect.centery
        return {'settings_bg': settings_bg_rect, 'back_button': back_button_rect, 'sound_slider': sound_slider_rect, 'sound_handle': sound_handle_rect}

    def render_settings_screen(self, temp_volume, ui_elements):
        self.render_background()
        self.ui_manager.draw_overlay((0, 0, 0, 150))
        fonts = {
            'title': self.fonts['title_large'], 
            'option': self.fonts['body_large'], 
            'button': self.fonts['button_small']
        }
        
        settings_bg_rect, sound_slider_rect = ui_elements['settings_bg'], ui_elements['sound_slider']
        sound_handle_rect = ui_elements['sound_handle']

        sound_handle_rect.centerx = sound_slider_rect.left + (sound_slider_rect.width * temp_volume)

        self.ui_manager.draw_panel(settings_bg_rect, (230, 230, 230, 220), BLACK, 3, 15)
        title_surf = fonts['title'].render("설정", True, BLACK)
        self.screen.blit(title_surf, title_surf.get_rect(center=(settings_bg_rect.centerx, settings_bg_rect.top + scale_y(70))))
        
        sound_text_surf = fonts['option'].render("사운드", True, BLACK)
        self.screen.blit(sound_text_surf, sound_text_surf.get_rect(midright=(sound_slider_rect.left - scale_x(20), sound_slider_rect.centery)))
        self.ui_manager.draw_slider(sound_slider_rect, sound_handle_rect, WHITE, (150, 150, 150), BLACK)
        self.ui_manager.draw_interactive_button(ui_elements['back_button'], "뒤로 가기", fonts['button'], (220, 220, 220), WHITE, (100, 100, 100))

    def prepare_ranking_assets(self):
        title_rect_center_y = scale_y(120)
        left_arrow = pygame.Rect(0, 0, scale_x(60), scale_y(60)); left_arrow.centery = title_rect_center_y; left_arrow.right = self.width / 2 - scale_x(250)
        right_arrow = pygame.Rect(0, 0, scale_x(60), scale_y(60)); right_arrow.centery = title_rect_center_y; right_arrow.left = self.width / 2 + scale_x(250)
        back_button = pygame.Rect(scale_x(30), scale_y(30), scale_x(180), scale_y(70))
        return left_arrow, right_arrow, back_button
    
    def render_ranking_screen(self, current_stage, ranking_data):
        self.render_background(); self.ui_manager.draw_overlay((0, 0, 0, 150))
        fonts = {
            'title': self.fonts['title_small'], 
            'rank': self.fonts['body_small'], 
            'arrow': self.fonts['title_small'], 
            'button': self.fonts['body_small']
        }
        title_text = f"랭킹 (스테이지 {current_stage})"; title_rect_center_y = scale_y(120)
        self.ui_manager.draw_centered_text_with_shadow(title_text, fonts['title'], WHITE, BLACK, (self.width / 2, title_rect_center_y))
        left_arrow, right_arrow, back_button = self.prepare_ranking_assets()
        mouse_pos = pygame.mouse.get_pos()
        left_color = WHITE if left_arrow.collidepoint(mouse_pos) else GRAY; right_color = WHITE if right_arrow.collidepoint(mouse_pos) else GRAY
        self.screen.blit(fonts['arrow'].render("<", True, left_color), fonts['arrow'].render("<", True, left_color).get_rect(center=left_arrow.center))
        self.screen.blit(fonts['arrow'].render(">", True, right_color), fonts['arrow'].render(">", True, right_color).get_rect(center=right_arrow.center))
        start_y = title_rect_center_y + scale_y(100)
        if not ranking_data: self.screen.blit(fonts['rank'].render("기록이 없습니다", True, GRAY), fonts['rank'].render("기록이 없습니다", True, GRAY).get_rect(center=(self.width / 2, start_y + scale_y(100))))
        else:
            for i, record in enumerate(ranking_data):
                entry_rect = pygame.Rect(0, 0, self.width - scale_x(300), scale_y(70)); entry_rect.center = (self.width / 2, start_y + i * scale_y(80))
                self.ui_manager.draw_panel(entry_rect, (240, 240, 240, 200), BLACK, 2, 10)
                self.screen.blit(fonts['rank'].render(f"#{i+1}", True, BLACK), fonts['rank'].render(f"#{i+1}", True, BLACK).get_rect(center=(entry_rect.left + scale_x(50), entry_rect.centery)))
                self.screen.blit(fonts['rank'].render(record["name"], True, BLACK), fonts['rank'].render(record["name"], True, BLACK).get_rect(midleft=(entry_rect.left + scale_x(110), entry_rect.centery)))
                self.screen.blit(fonts['rank'].render(f"{record['time']:.2f} 초", True, (50, 50, 50)), fonts['rank'].render(f"{record['time']:.2f} 초", True, (50,50,50)).get_rect(center=(entry_rect.centerx, entry_rect.centery)))
                self.screen.blit(fonts['rank'].render(f"사용: {record['blocks']}개", True, (50, 50, 50)), fonts['rank'].render(f"사용: {record['blocks']}개", True, (50,50,50)).get_rect(midright=(entry_rect.right - scale_x(160), entry_rect.centery)))
                self.screen.blit(fonts['rank'].render(f"먹힘: {record.get('eaten', 0)}개", True, (50, 50, 50)), fonts['rank'].render(f"먹힘: {record.get('eaten', 0)}개", True, (50,50,50)).get_rect(midright=(entry_rect.right - scale_x(30), entry_rect.centery)))
        self.ui_manager.draw_interactive_button(back_button, "뒤로 가기", fonts['button'], (220, 220, 220), WHITE, (100, 100, 100))

    def render_stage_select(self, stage_rects, selected_stage_num, back_button_rect, scroll_y, scroll_bar_rect, content_height, view_height, highest_unlocked: int):
        self.render_background()
        fonts = {
            'title': self.fonts['title_large'], 
            'stage_title': self.fonts['button_small'],
            'stage_num': self.fonts['body_large'],
            'feature': self.fonts['body_small'],
            'popup_title': self.fonts['title_small'],
            'popup_info': self.fonts['body_large']
        }
        
        self.ui_manager.draw_centered_text_with_shadow("스테이지 선택", fonts['title'], WHITE, BLACK, (self.width / 2, scale_y(100)))

        for i, rect in enumerate(stage_rects):
            stage_num = i + 1
            visible_rect = rect.move(0, -scroll_y)

            if visible_rect.bottom > scale_y(180) and visible_rect.top < self.height:
                is_locked = stage_num > highest_unlocked
                is_hovered = visible_rect.collidepoint(pygame.mouse.get_pos()) and not is_locked

                base_color = (240, 240, 240)
                hover_color = WHITE
                self.ui_manager.draw_interactive_button(visible_rect, "", fonts['stage_title'], base_color, hover_color if is_hovered else base_color, (100,100,100))

                text_color = BLACK if not is_locked else GRAY

                num_text = fonts['stage_num'].render(f"{stage_num}", True, text_color)
                self.screen.blit(num_text, num_text.get_rect(center=(visible_rect.left + scale_x(60), visible_rect.centery)))

                stage_name = STAGE_DATA.get(str(stage_num), {}).get("name", f"스테이지 {stage_num}")
                name_text = fonts['stage_title'].render(stage_name, True, text_color)
                self.screen.blit(name_text, name_text.get_rect(midleft=(visible_rect.left + scale_x(120), visible_rect.centery)))
                
                if is_locked:
                    self.ui_manager.draw_disabled_overlay(visible_rect, 100)
                    padlock_area = pygame.Rect(0, 0, scale_x(50), scale_y(50))
                    padlock_area.centery = visible_rect.centery
                    padlock_area.right = visible_rect.right - scale_x(30)
                    self.ui_manager.draw_padlock(padlock_area, (40, 40, 40))

        self.ui_manager.draw_scroll_bar(scroll_bar_rect, content_height, view_height, scroll_y)

        if selected_stage_num:
            self.ui_manager.draw_overlay((0, 0, 0, 180))
            popup_rect = pygame.Rect(0, 0, scale_x(600), scale_y(400)); popup_rect.center = (self.width / 2, self.height / 2)
            self.ui_manager.draw_panel(popup_rect, (230, 230, 230, 220), BLACK, 3, 15)
            self.ui_manager.draw_centered_text(f"스테이지 {selected_stage_num}", fonts['popup_title'], BLACK, (popup_rect.centerx, popup_rect.top + scale_y(80)))
            
            difficulty = "보통"
            self.ui_manager.draw_centered_text(f"난이도: {difficulty}", fonts['popup_info'], BLACK, (popup_rect.centerx, popup_rect.centery - scale_y(20)))
            
            start_button = pygame.Rect(0, 0, scale_x(300), scale_y(80)); start_button.center = (popup_rect.centerx, popup_rect.bottom - scale_y(80))
            self.ui_manager.draw_interactive_button(start_button, "게임 시작", fonts['popup_info'], WHITE, (240, 240, 240), (100,100,100))

        self.ui_manager.draw_interactive_button(back_button_rect, "뒤로 가기", fonts['feature'], (220, 220, 220), WHITE, (100, 100, 100))
    
    def render_game_ui(self, ui_animals: list, dragging_animal: Optional[dict], animal_usage_counts: dict, stats: dict, fonts: dict, restart_button_rect: pygame.Rect, start_time: int):
        self.ui_manager.draw_game_ui_panel(pygame.Rect(0, self.height - scale_y(120), self.width, scale_y(120)))
        
        count_font = self.fonts['count']

        for ui_animal in ui_animals:
            if ui_animal.image:
                self.screen.blit(ui_animal.image, ui_animal.rect)
            else:
                pygame.draw.rect(self.screen, ui_animal.icon_color, ui_animal.rect)
                if fonts and 'small' in fonts:
                    self.ui_manager.draw_centered_text(ui_animal.name, fonts['small'], BLACK, ui_animal.rect.center)
            
            count = animal_usage_counts.get(ui_animal.name, 0)
            if count == 0:
                self.ui_manager.draw_disabled_overlay(ui_animal.rect)

            count_surf = count_font.render(str(count), True, WHITE)
            count_shadow_surf = count_font.render(str(count), True, BLACK)
            count_rect = count_surf.get_rect(bottomright=(ui_animal.rect.right - scale_x(5), ui_animal.rect.bottom - scale_y(5)))
            shadow_rect = count_shadow_surf.get_rect(bottomright=(count_rect.right + scale_x(1), count_rect.bottom + scale_y(1)))
            
            self.screen.blit(count_shadow_surf, shadow_rect)
            self.screen.blit(count_surf, count_rect)

        if dragging_animal:
            self.render_dragging_animal(dragging_animal)

        button_font = self.fonts['count']
        self.ui_manager.draw_interactive_button(restart_button_rect, "다시 시작", button_font, (220, 220, 220), WHITE, (100, 100, 100))

        elapsed_seconds = (pygame.time.get_ticks() - start_time) / 1000
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        time_str = f"{minutes:02}:{seconds:02}"

        timer_font = self.fonts['timer']
        time_surf = timer_font.render(time_str, True, WHITE)
        time_shadow_surf = timer_font.render(time_str, True, (0, 0, 0, 150))

        time_rect = time_surf.get_rect(topright=(self.width - scale_x(20), scale_y(15)))
        shadow_rect = time_shadow_surf.get_rect(topright=(time_rect.right + scale_x(2), time_rect.top + scale_y(2)))
        
        self.screen.blit(time_shadow_surf, shadow_rect)
        self.screen.blit(time_surf, time_rect)

    def render_dragging_animal(self, dragging_animal: dict):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        drop_zone_width = scale_x(680)
        drop_zone_x = (self.width / 2) - (drop_zone_width / 2)
        drop_zone = pygame.Rect(drop_zone_x, scale_y(30), drop_zone_width, scale_y(130))
        pygame.draw.rect(self.screen, (0, 255, 0, 50), drop_zone, int(scale_x(2)))
        if dragging_animal["image"]:
            rotated_image = pygame.transform.rotate(dragging_animal["image"], -dragging_animal["angle_degrees"])
            self.screen.blit(rotated_image, rotated_image.get_rect(center=(mouse_x, mouse_y)))
        else:
            rect = pygame.Rect(mouse_x - scale_x(30), mouse_y - scale_y(30), scale_x(60), scale_y(60))
            pygame.draw.rect(self.screen, (255,0,255), rect, int(scale_x(5)))

    def render_ending_scene(self, stage_num: int, used: int, eaten: int, time_str: str, next_button_rect: pygame.Rect):
        self.ui_manager.draw_overlay((240, 240, 240, 220))
        fonts = {
            'title': self.fonts['title_large'], 
            'stats': self.fonts['title_medium'], 
            'button': self.fonts['body_large']
        }
        self.ui_manager.draw_centered_text(f"스테이지 {stage_num} 클리어", fonts['title'], BLACK, (self.width / 2, self.height / 2 - scale_y(200)))
        self.ui_manager.draw_centered_text(f"사용한 블럭: {used}개", fonts['stats'], BLACK, (self.width / 2, self.height / 2 - scale_y(50)))
        self.ui_manager.draw_centered_text(f"먹힌 블럭: {eaten}개", fonts['stats'], BLACK, (self.width / 2, self.height / 2 + scale_y(50)))
        self.ui_manager.draw_centered_text(f"클리어 시간: {time_str}", fonts['stats'], BLACK, (self.width / 2, self.height / 2 + scale_y(150)))
        self.ui_manager.draw_interactive_button(next_button_rect, "다음", fonts['button'], (220, 220, 220), WHITE, (100, 100, 100))

    def render_game_over_screen(self, fonts: dict, menu_button_rect: pygame.Rect):
        self.ui_manager.draw_overlay((0, 0, 0, 180))
        fonts_ext = {
            'title': self.fonts['title_large'], 
            'button': self.fonts['body_large']
        }
        self.ui_manager.draw_centered_text_with_shadow("GAME OVER", fonts_ext['title'], RED, (50,0,0), (self.width / 2, self.height / 2 - scale_y(50)))
        self.ui_manager.draw_interactive_button(menu_button_rect, "메인 메뉴로", fonts_ext['button'], (220, 220, 220), WHITE, (100, 100, 100))