class Pokemon:
    def __init__(self, id, nome, id_name, stat, sprite, shadow_sprite = None):
        self.id=id
        self.nome=nome
        self.id_name=id_name
        self.stat=stat
        self.sprite=sprite
        self.shadow_sprite=shadow_sprite