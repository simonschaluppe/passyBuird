from typing import Protocol
import pygame as pg

class Camera(Protocol):
    def project(self, sprite):
        ...
    
    def game_coords(self, screen_coords:pg.Vector2) -> pg.Vector2:
        ...

    def screen_coords(self, game_coords:pg.Vector2) -> pg.Vector2:
        ...

    def view_rect(self):
        """camera view rectangle in game coordinates"""
        ...

class Camera2D(Camera):
    def __init__(self, 
                 surface:pg.Surface=None,  
                 game_world_position=(0,0),
                 zoom:tuple=(1,1),
                 ):
        self.screen = surface
        self.screen_width, self.screen_height = surface.get_size()
        self.proj_center = pg.Vector2(self.screen_width//2,self.screen_height//2)
        self.position = pg.Vector2(*game_world_position)
        self.zoom_level = zoom
        self.follows = None
        self.relative_speed = pg.Vector2(0,0)

    def follow(self, Node, maxdist=1):
        self.maxdist = maxdist
        self.follows = Node

    def update(self):
        if self.follows is not None:
            screendist = self.screen_coords(self.follows.position) - self.screen_coords(self.position)
            gap = screendist.length() - self.maxdist
            if gap > 0: 
                self.position.move_towards_ip(self.follows.position, gap)
    
    @property
    def view_rect(self):
        rect = pg.Rect(
            self.position.x - self.screen_width / 2/self.zoom_level[0], 
            self.position.y - self.screen_height /2/self.zoom_level[1], 
            self.position.x + self.screen_width / 2/self.zoom_level[0] ,
            self.position.y + self.screen_height /2/self.zoom_level[1],
        )
        return rect
    
    def project(self, sprite:pg.sprite.Sprite):
        image = pg.transform.scale_by(sprite.image, self.zoom_level) 
        rect = self.project_rect(sprite.rect)
        return image, rect
    
    def project_rect(self, rect:pg.Rect) -> pg.Rect: # TODO: this should just be in screen coords
        v_game = pg.Vector2(rect.center[0], rect.center[1])
        v_proj = self.screen_coords(v_game)
        dx =  v_proj.x - v_game.x 
        dy = v_proj.y - v_game.y 
        # dx = self.proj_loc_on_screen_x + projector_x - game_x 
        # dy = self.proj_loc_on_screen_y + projector_y - game_y
        screenrect = rect.move(dx,dy)
        screenrect.scale_by_ip(*self.zoom_level)
        return screenrect
    
    def screen_coords(self, game_coords:tuple[float, float]) -> pg.Vector2:
        v_proj = pg.Vector2(*game_coords) - self.position
        projector_x = self.proj_center.x + v_proj.x * self.zoom_level[0]
        projector_y = self.proj_center.y - v_proj.y * self.zoom_level[1]
        v_proj = pg.Vector2(projector_x, projector_y)
        return v_proj

    def game_coords(self, screen_coords:pg.Vector2) -> pg.Vector2:
        game_x = (screen_coords.x - self.proj_center.x)/ self.zoom_level[0]
        game_y = -(screen_coords.y - self.proj_center.y)/ self.zoom_level[1]
        v_game = pg.Vector2(game_x, game_y)
        v_game = v_game + self.position
        return v_game

    def zoom(self, factor):
        x, y = self.zoom_level
        self.zoom_level = (x * factor, y * factor)

    def move(self, xy_tuple):
        #should be in screen coordinates, not in game coordinates
        self.position += pg.Vector2(*xy_tuple)

    def reset(self):
        self.zoom_level = (1,1)
        self.position = pg.Vector2(0,0)
        if self.follows is not None:
            print("resetting camera to follow")
            self.position.xy = self.follows.position.xy

    def __repr__(self) -> str:
        return f"Camera(screen={self.screen.get_size()}, game_pos={self.position}, {self.zoom_level=})"
