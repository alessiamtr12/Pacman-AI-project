import pygame


class Button:
    def __init__(self, x, y, width, height, text,
                 color=(70, 70, 70),
                 hover_color=(100, 100, 100),
                 text_color=(255, 255, 255)):

        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 32)

    def draw(self, screen):

        # check if the mouse is hovering over the button
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        # draw the button rectangle
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect)

        # add a simple border
        pygame.draw.rect(screen, (30, 30, 30), self.rect, 2)

        # draw the text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event) -> bool:

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for left mouse click
            if event.button == 1 and self.is_hovered:
                return True
        return False