from datetime import datetime

class BaseModel:
    def __init__(self, id=None, create_time=None, update_time=None, delete_time=None, **kwargs):
        now = datetime.now().isoformat()
        self.id = id  # 可用自增或uuid
        self.create_time = create_time or now
        self.update_time = update_time or now
        self.delete_time = delete_time  # 默认为None
        
        # 设置其他属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        result = {
            'id': self.id,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'delete_time': self.delete_time
        }
        # 添加其他属性
        for key, value in self.__dict__.items():
            if key not in result:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data):
        # 分离基础字段和其他字段
        base_fields = {
            'id': data.get('id'),
            'create_time': data.get('create_time'),
            'update_time': data.get('update_time'),
            'delete_time': data.get('delete_time')
        }
        # 获取其他字段
        other_fields = {k: v for k, v in data.items() if k not in base_fields}
        # 合并所有字段
        return cls(**base_fields, **other_fields) 