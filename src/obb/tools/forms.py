import datetime


class BaseDataForm:
    def read_data(self, model):
        for key in self.data:
            value = getattr(model, key, None)
            field = getattr(self, key, None)
            if value and field:
                if isinstance(value, datetime.datetime):
                    # Todo: TZ
                    offset = datetime.datetime.now() - datetime.datetime.utcnow()
                    value = value + offset

                setattr(field, 'data', value)

    def write_data(self, model):
        for key in self.data:
            if not hasattr(model, key):
                continue

            field = getattr(self, key, None)
            if field is None:
                continue

            value = getattr(field, 'data')
            if isinstance(value, datetime.datetime):
                # Todo: TZ
                offset = datetime.datetime.now() - datetime.datetime.utcnow()
                value = value - offset

            setattr(model, key, value)
