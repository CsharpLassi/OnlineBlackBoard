class BaseDataForm:
    def read_data(self, model):
        for key in self.data:
            value = getattr(model, key, None)
            field = getattr(self, key, None)
            if value and field:
                setattr(field, 'data', value)

    def write_data(self, model):
        for key in self.data:
            if not hasattr(model, key):
                continue

            field = getattr(self, key, None)
            if field is None:
                continue
            value = getattr(field, 'data')
            setattr(model, key, value)
