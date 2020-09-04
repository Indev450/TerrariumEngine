class Camera:
    instance = None

    @classmethod
    def init(cls):
        cls.instance = Camera()

    @classmethod
    def get(cls):
        return cls.instance

    def __init__(self, offset_x=0, offset_y=0):
        self.x = 0
        self.y = 0
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.obj = None
        self.update_position()

    def update_position(self):
        if self.obj is None:
            return
        self.x = self.obj.rect.x
        self.y = self.obj.rect.y

    def set_obj(self, obj):
        self.obj = obj
        self.update_position()

    def move_offset(self, x, y):
        self.offset_x += x
        self.offset_y += y

    def set_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def get_position(self):
        return self.x - self.offset_x, self.y - self.offset_y
