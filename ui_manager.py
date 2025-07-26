# ui_manager.py

import pygame
import math
from settings import *

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_cache = {}

    def draw_disabled_overlay(self, rect, alpha=180):
        """rect 위에 반투명 회색 오버레이를 그려 비활성화 효과를 줌"""
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill((100, 100, 100, alpha))
        self.screen.blit(overlay, rect.topleft)
        
    def get_font(self, font_name, size, bold=False, italic=False):
        key = (font_name, size, bold, italic)
        if key not in self.font_cache: self.font_cache[key] = pygame.font.SysFont(font_name, size, bold=bold, italic=italic)
        return self.font_cache[key]

    def draw_scroll_bar(self, rect, content_height, view_height, scroll_y):
        pygame.draw.rect(self.screen, GRAY, rect, 0, int(scale_x(8)))
        if content_height > view_height:
            handle_height = max(scale_y(20), view_height * (view_height / content_height))
            scroll_ratio = scroll_y / (content_height - view_height)
            handle_y = rect.y + scroll_ratio * (rect.height - handle_height)
            handle_rect = pygame.Rect(rect.x, handle_y, rect.width, handle_height)
            pygame.draw.rect(self.screen, LIGHT_GRAY, handle_rect, 0, int(scale_x(8)))
            pygame.draw.rect(self.screen, (100,100,100), handle_rect, int(scale_x(2)), int(scale_x(8)))

    def draw_gear(self, rect, color):
        center = rect.center
        outer_radius, inner_radius, hole_radius = rect.width / 2 * 0.9, rect.width / 2 * 0.9 * 0.7, rect.width / 2 * 0.9 * 0.4
        points = []
        for i in range(8):
            angle1, angle2 = math.radians(i * 45 - 11.25), math.radians(i * 45 + 11.25)
            points.append((center[0] + inner_radius * math.cos(angle1), center[1] + inner_radius * math.sin(angle1)))
            points.append((center[0] + outer_radius * math.cos(angle1), center[1] + outer_radius * math.sin(angle1)))
            points.append((center[0] + outer_radius * math.cos(angle2), center[1] + outer_radius * math.sin(angle2)))
            points.append((center[0] + inner_radius * math.cos(angle2), center[1] + inner_radius * math.sin(angle2)))
        for i in range(0, len(points), 4): pygame.draw.polygon(self.screen, color, points[i:i+4])
        pygame.draw.circle(self.screen, color, center, inner_radius)
        pygame.draw.circle(self.screen, WHITE, center, hole_radius)
    
    def draw_interactive_button(self, rect, text, font, base_color, hover_color, shadow_color):
        is_hovered = rect.collidepoint(pygame.mouse.get_pos())
        shadow_rect = rect.move(scale_x(5), scale_y(5))
        pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=int(scale_x(12)))
        pygame.draw.rect(self.screen, hover_color if is_hovered else base_color, rect, border_radius=int(scale_x(10)))
        pygame.draw.rect(self.screen, BLACK, rect, int(scale_x(2)), border_radius=int(scale_x(10)))
        text_surf = font.render(text, True, BLACK)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
        return is_hovered
    
    def draw_text_input(self, rect, text, font, placeholder_text, placeholder_font, is_active):
        pygame.draw.rect(self.screen, GRAY, rect, 0, int(scale_x(5)))

        padding = scale_x(15)
        clip_rect = rect.inflate(-padding * 2, 0)
        self.screen.set_clip(clip_rect)

        # [최종 수정] 입력창이 활성화(active)되었거나, 글자가 있으면(text) 입력 내용을 표시
        if is_active or text:
            # 사용자가 입력한 텍스트를 그립니다.
            text_surf = font.render(text, True, BLACK)
            text_rect = text_surf.get_rect()

            if text_rect.width > clip_rect.width:
                text_rect.midright = (clip_rect.right, clip_rect.centery)
            else:
                text_rect.midleft = (clip_rect.left, clip_rect.centery)
            
            self.screen.blit(text_surf, text_rect)

            # 입력창이 활성화 상태일 때만 커서를 그립니다.
            if is_active:
                cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 1
                if cursor_visible:
                    # 텍스트가 없을 때와 있을 때의 커서 위치를 계산합니다.
                    if text:
                        cursor_x = text_rect.right + scale_x(2)
                    else:
                        cursor_x = text_rect.left
                    
                    cursor_height = font.get_height() * 0.9
                    cursor_top = rect.centery - cursor_height / 2
                    cursor_bottom = rect.centery + cursor_height / 2
                    pygame.draw.line(self.screen, BLACK, (cursor_x, cursor_top), (cursor_x, cursor_bottom), int(scale_x(2)))
        else:
            # 입력창이 비활성화 상태이고, 글자도 없으면 안내 문구 표시
            placeholder_surf = placeholder_font.render(placeholder_text, True, PLACEHOLDER_COLOR)
            placeholder_rect = placeholder_surf.get_rect(midleft=(clip_rect.left, clip_rect.centery))
            self.screen.blit(placeholder_surf, placeholder_rect)

        self.screen.set_clip(None)
        pygame.draw.rect(self.screen, ACTIVE_BORDER_COLOR if is_active else GRAY, rect, int(scale_x(3)), int(scale_x(5)))
    
    def draw_panel(self, rect, background_color, border_color, border_width=3, border_radius=15):
        border_width = int(scale_x(border_width))
        border_radius = int(scale_x(border_radius))
        pygame.draw.rect(self.screen, background_color, rect, 0, border_radius)
        if border_width > 0: pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius)

    def draw_overlay(self, color_alpha):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA); overlay.fill(color_alpha)
        self.screen.blit(overlay, (0, 0))

    def draw_centered_text(self, text, font, color, center_pos):
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, text_surf.get_rect(center=center_pos))

    def draw_centered_text_with_shadow(self, text, font, text_color, shadow_color, center_pos, offset=(3,3)):
        scaled_offset = (scale_x(offset[0]), scale_y(offset[1]))
        shadow_surf = font.render(text, True, shadow_color)
        text_surf = font.render(text, True, text_color)
        self.screen.blit(shadow_surf, shadow_surf.get_rect(center=(center_pos[0] + scaled_offset[0], center_pos[1] + scaled_offset[1])))
        self.screen.blit(text_surf, text_surf.get_rect(center=center_pos))

    def draw_slider(self, slider_rect, handle_rect, handle_color, track_color, border_color):
        pygame.draw.rect(self.screen, track_color, slider_rect, 0, int(scale_x(8)))
        pygame.draw.rect(self.screen, handle_color, handle_rect, 0, int(scale_x(5)))
        pygame.draw.rect(self.screen, border_color, handle_rect, int(scale_x(2)), int(scale_x(5)))
    
    def draw_circular_button(self, center, radius, color, text, font, text_color, hover_effect=True):
        is_hovered = math.sqrt((pygame.mouse.get_pos()[0] - center[0])**2 + (pygame.mouse.get_pos()[1] - center[1])**2) < radius
        draw_radius = radius * 1.1 if hover_effect and is_hovered else radius
        pygame.draw.circle(self.screen, BLACK, center, draw_radius + scale_x(4))
        pygame.draw.circle(self.screen, color, center, draw_radius)
        self.draw_centered_text(text, font, text_color, center)
        return is_hovered

    def draw_game_ui_panel(self, rect, alpha=180):
        ui_panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA); ui_panel.fill((200, 200, 200, alpha))
        self.screen.blit(ui_panel, rect.topleft)

    def draw_scrollable_text(self, text_surface, view_rect, scroll_y):
        self.screen.blit(text_surface, view_rect.topleft, (0, scroll_y, view_rect.width, view_rect.height))
    
    def create_text_surface(self, lines, line_spacing=5):
        if not lines: return pygame.Surface((1, 1), pygame.SRCALPHA)
        surfaces = [font.render(text, True, color) for text, font, color in lines]
        total_height = sum(s.get_height() for s in surfaces) + max(0, len(surfaces) - 1) * line_spacing
        max_width = max(s.get_width() for s in surfaces)
        surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        y_offset = 0
        for surf in surfaces:
            surface.blit(surf, (0, y_offset)); y_offset += surf.get_height() + line_spacing
        return surface