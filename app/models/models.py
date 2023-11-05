class Pokemon:
    def __init__(self, id, nome, stat, sprite, shadow_sprite = None):
        self.id=id
        self.nome=nome
        self.stat=stat
        self.sprite=sprite
        self.shadow_sprite=shadow_sprite