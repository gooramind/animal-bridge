# tilemap_renderer.py (수정 완료)

import pygame
import os
import time
from typing import List, Dict, Optional
from settings import *
from settings import resource_path
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class TerrainRenderer:
    """개별 타일 이미지 기반 지형 렌더러"""

    def __init__(self, assets_path: str = None):
        if assets_path is None:
            # 이제 resource_path를 사용하므로 이 부분은 기준 경로 역할만 합니다.
            assets_path = os.path.join("assets", "Tilemap")

        self.assets_path = assets_path
        self.tiles: Dict[str, pygame.Surface] = {}  # 원본 타일 데이터
        self.scaled_tiles: Dict[str, pygame.Surface] = {}  # 스케일링된 타일 데이터
        
        self.original_tile_size = BASE_TILE_SIZE
        self.current_tile_size = get_current_tile_size()

        # 깃발 애니메이션 관련
        self.flag_animation_timer = 0
        self.flag_frame_duration = 300  # 300ms
        self.current_flag_frame = 0

        self._load_tiles()
        self._scale_tiles()

    def _load_tiles(self):
        """개별 타일 이미지들을 로드 (원본 크기로)"""
        tile_files = {
            # Grass 계열 (왼쪽, 중앙, 오른쪽)
            'grass_left': 'tile_0021.png',
            'grass_center': 'tile_0022.png',
            'grass_right': 'tile_0023.png',

            # Dirt 계열 (왼쪽, 중앙, 오른쪽)
            'dirt_left': 'tile_0121.png',
            'dirt_center': 'tile_0122.png',
            'dirt_right': 'tile_0123.png',

            # 브릿지
            'bridge': 'tile_0029.png',

            # 깃발 애니메이션 프레임
            'flag_frame1': 'tile_0111.png',
            'flag_frame2': 'tile_0112.png'
        }

        for tile_name, filename in tile_files.items():
            # resource_path를 사용하여 파일의 전체 경로를 가져옵니다.
            file_path = resource_path(os.path.join(self.assets_path, filename))
            try:
                original_surface = pygame.image.load(file_path).convert_alpha()
                self.tiles[tile_name] = original_surface
                print(f"✓ 타일 로드 성공: {filename}")

            except pygame.error as e:
                print(f"✗ 타일 로드 실패: {filename} - {e}")
                fallback_surface = pygame.Surface((self.original_tile_size, self.original_tile_size))
                fallback_surface.fill((255, 0, 255))
                self.tiles[tile_name] = fallback_surface

    def _scale_tiles(self):
        """현재 해상도에 맞게 타일들을 스케일링"""
        self.scaled_tiles.clear()
        for tile_name, original_tile in self.tiles.items():
            scaled_surface = pygame.transform.scale(
                original_tile,
                (self.current_tile_size, self.current_tile_size)
            )
            self.scaled_tiles[tile_name] = scaled_surface

    def update_resolution(self):
        """해상도 변경 시 타일 크기 업데이트"""
        self.current_tile_size = get_current_tile_size()
        self._scale_tiles()

    def update(self):
        """깃발 애니메이션 업데이트"""
        current_time = pygame.time.get_ticks()
        if current_time - self.flag_animation_timer >= self.flag_frame_duration:
            self.current_flag_frame = 1 - self.current_flag_frame
            self.flag_animation_timer = current_time

    def _get_terrain_type_and_position(self, terrain_rect: pygame.Rect, terrain_index: int, total_terrains: int) -> str:
        """지형 인덱스에 따라 지형 타입을 결정"""
        if total_terrains == 2:
            return 'bank'
        elif total_terrains == 3:
            return 'bridge' if terrain_index == 1 else 'bank'
        elif total_terrains == 4:
            return 'bridge' if terrain_index in [1, 2] else 'bank'
        else:
            return 'bank'

    def _render_bank_terrain(self, screen: pygame.Surface, terrain_rect: pygame.Rect, is_left_bank: bool = True):
        """뱅크 지형 렌더링 (1행은 grass, 2행 이상은 dirt)"""
        tile_width = self.current_tile_size
        tile_height = self.current_tile_size

        tiles_horizontal = (terrain_rect.width + tile_width - 1) // tile_width
        tiles_vertical = (terrain_rect.height + tile_height - 1) // tile_height

        for row in range(tiles_vertical):
            for col in range(tiles_horizontal):
                x = terrain_rect.x + col * tile_width
                y = terrain_rect.y + row * tile_height

                if row == 0:
                    tile_name = 'grass_center'
                    if col == 0: tile_name = 'grass_left'
                    elif col == tiles_horizontal - 1: tile_name = 'grass_right'
                else:
                    tile_name = 'dirt_center'
                    if col == 0: tile_name = 'dirt_left'
                    elif col == tiles_horizontal - 1: tile_name = 'dirt_right'

                if tile_name in self.scaled_tiles:
                    screen.blit(self.scaled_tiles[tile_name], (x, y))

    def _render_bridge_terrain(self, screen: pygame.Surface, terrain_rect: pygame.Rect):
        """브릿지 지형 렌더링 (29번 블록으로 채움)"""
        tile_width = self.current_tile_size
        tile_height = self.current_tile_size

        tiles_horizontal = (terrain_rect.width + tile_width - 1) // tile_width
        tiles_vertical = (terrain_rect.height + tile_height - 1) // tile_height

        bridge_tile = self.scaled_tiles.get('bridge')
        if not bridge_tile:
            pygame.draw.rect(screen, (139, 69, 19), terrain_rect)
            return

        for row in range(tiles_vertical):
            for col in range(tiles_horizontal):
                x = terrain_rect.x + col * tile_width
                y = terrain_rect.y + row * tile_height
                screen.blit(bridge_tile, (x, y))

    def render_terrain(self, screen: pygame.Surface, terrain_rects: List[pygame.Rect]):
        """지형 렌더링 메인 함수"""
        total_terrains = len(terrain_rects)
        for i, rect in enumerate(terrain_rects):
            terrain_type = self._get_terrain_type_and_position(rect, i, total_terrains)
            if terrain_type == 'bridge':
                self._render_bridge_terrain(screen, rect)
            else:
                self._render_bank_terrain(screen, rect, is_left_bank=(i == 0))

    def render_flag(self, screen: pygame.Surface, goal_pos: tuple):
        """깃발 렌더링 (애니메이션, 원본 크기)"""
        flag_frame_name = f'flag_frame{self.current_flag_frame + 1}'
        flag_tile = self.scaled_tiles.get(flag_frame_name)

        if flag_tile:
            flag_size = self.current_tile_size
            flag_x = scale_x(goal_pos[0]) - flag_size // 2
            flag_y = scale_y(goal_pos[1]) - flag_size
            screen.blit(flag_tile, (flag_x, flag_y))
        else:
            flag_x, flag_y = scale_x(goal_pos[0]), scale_y(goal_pos[1])
            pole_height, pole_width = scale_y(60), scale_x(5)
            pole_rect = pygame.Rect(flag_x, flag_y - pole_height, pole_width, pole_height)
            cloth_points = [
                (flag_x + pole_width, flag_y - pole_height),
                (flag_x + pole_width, flag_y - pole_height + scale_y(25)),
                (flag_x + pole_width + scale_x(40), flag_y - pole_height + scale_y(12.5))
            ]
            pygame.draw.rect(screen, (192, 192, 192), pole_rect)
            pygame.draw.polygon(screen, (220, 20, 60), cloth_points)

    def render_ground_floor(self, screen: pygame.Surface):
        """맨 아래 바닥에 dirt 블럭 한 줄 배치"""
        dirt_center = self.scaled_tiles.get('dirt_center')
        if not dirt_center: return

        ground_y = HEIGHT - self.current_tile_size
        tiles_horizontal = (WIDTH + self.current_tile_size - 1) // self.current_tile_size
        for col in range(tiles_horizontal):
            x = col * self.current_tile_size
            tile = self.scaled_tiles.get('dirt_left') if col == 0 else self.scaled_tiles.get('dirt_right') if col == tiles_horizontal - 1 else dirt_center
            if tile: screen.blit(tile, (x, ground_y))

    def render_bank_extensions(self, screen: pygame.Surface, terrain_rects: List[pygame.Rect]):
        """뱅크 지형의 아래에 2줄의 dirt 타일을 추가 배치"""
        dirt_center = self.scaled_tiles.get('dirt_center')
        if not dirt_center: return

        total_terrains = len(terrain_rects)
        for i, rect in enumerate(terrain_rects):
            if self._get_terrain_type_and_position(rect, i, total_terrains) == 'bank':
                start_y = rect.bottom
                tiles_horizontal = rect.width // self.current_tile_size
                for row in range(2):
                    for col in range(tiles_horizontal):
                        x = rect.x + col * self.current_tile_size
                        y = start_y + row * self.current_tile_size
                        tile = self.scaled_tiles.get('dirt_left') if col == 0 else self.scaled_tiles.get('dirt_right') if col == tiles_horizontal - 1 else dirt_center
                        if tile: screen.blit(tile, (x, y))

class BackgroundRenderer:
    """배경 렌더러 (단순 하늘색)"""
    def __init__(self):
        self.sky_color = (135, 206, 235)

    def render_background(self, screen: pygame.Surface):
        screen.fill(self.sky_color)

class TileMapManager:
    """타일맵 통합 관리자"""
    def __init__(self, assets_path: str = None):
        self.terrain_renderer = TerrainRenderer(assets_path)
        self.background_renderer = BackgroundRenderer()

    def update(self):
        self.terrain_renderer.update()

    def update_resolution(self):
        """해상도 변경 시 타일 크기 업데이트"""
        update_tile_size()
        self.terrain_renderer.update_resolution()

    def render_terrain(self, screen: pygame.Surface, terrain_rects: List[pygame.Rect]):
        """지형 렌더링"""
        self.background_renderer.render_background(screen)
        self.terrain_renderer.render_bank_extensions(screen, terrain_rects)
        self.terrain_renderer.render_terrain(screen, terrain_rects)

    def render_background(self, screen: pygame.Surface):
        self.background_renderer.render_background(screen)

    def render_flag(self, screen: pygame.Surface, goal_pos: tuple):
        self.terrain_renderer.render_flag(screen, goal_pos)