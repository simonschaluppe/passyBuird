from collections import defaultdict
import pygame, sys

# Funcs/Classes ---------------------------------------------- #
def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

class Font():
    def __init__(self, path):
        self.spacing = 1
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';','°']
        font_img = pygame.image.load(path).convert()
        self.height = font_img.get_height()
        current_char_width = 0
        self.characters = {}
        character_count = 0
        for x in range(font_img.get_width()):
            c = font_img.get_at((x, 0))
            if c[0] == 127:
                char_img = clip(font_img, x - current_char_width, 0, current_char_width, self.height)
                self.characters[self.character_order[character_count]] = char_img.copy()
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1
        self.space_width = self.characters['A'].get_width()

    def render(self, surf, text, loc, size=None, color=(10,10,10)):
        if not size: size = self.height
        scale = int(size/self.height)
        small_surf = pygame.Surface((800,self.height))
        x_offset = 0
        for char in text:
            if char != ' ':
                small_surf.blit(self.characters[char], (x_offset, 0))
                x_offset += self.characters[char].get_width() + self.spacing
            else:
                x_offset += self.space_width + self.spacing
        text = pygame.transform.scale(small_surf, (800*scale, self.height*scale))
        colorbg= pygame.Surface(text.get_size())
        colorbg.fill(color)
        text.set_colorkey((255,0,0))
        colorbg.blit(text, (0,0))
        colorbg.set_colorkey((0,0,0))
        

        surf.blit(colorbg, (loc[0], loc[1]))

# Init ------------------------------------------------------- #

if __name__ == '__main__':
    #!/usr/bin/python3.4
    # Setup Python ----------------------------------------------- #


    # Setup pygame/window ---------------------------------------- #
    mainClock = pygame.time.Clock()
    from pygame.locals import *
    pygame.init()
    pygame.display.set_caption('game base')
    screen = pygame.display.set_mode((500, 500),0,32)

    my_font = Font('assets/fonts/small_font.png')
    my_big_font = Font('assets/fonts/large_font.png')

    
# Loop ------------------------------------------------------- #
while True:
    
    # Background --------------------------------------------- #
    screen.fill((0,232,0))


    my_font.render(screen, 'Hello World!', (20, 20))
    my_big_font.render(screen, 'Hello World! I am DaFluffyPotato.', (20, 40))
    my_big_font.render(screen, 'Hello World! I am Simono.', (20, 60), 200)
    my_font.render(screen, 'Hello World! I have °C.', (20, 120), 20)
    
    # Buttons ------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
                
    # Update ------------------------------------------------- #
    pygame.display.update()
    mainClock.tick(60)
    
