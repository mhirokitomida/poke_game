class Pokemon:
    def __init__(self, id, name, id_name, stat, sprite, shadow_sprite = None):
        self.id=id
        self.name=name
        self.id_name=id_name
        self.stat=stat
        self.sprite=sprite
        self.shadow_sprite=shadow_sprite