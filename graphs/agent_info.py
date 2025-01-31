class Agent():
    @property
    def endpoint(self):
        raise NotImplementedError("You must implement this.")
    @property
    def display_name(self):
        raise NotImplementedError("You must implement this.")
    @property
    def placeholder(self):
        raise NotImplementedError("You must implement this.")

    class Config(BaseModel):
        pass