import json
import os

FILE_PATH = "templates.json"

class TemplateManager:
    def __init__(self):
        self.templates = []
        self.load()

    def load(self):
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r") as f:
                self.templates = json.load(f)
        else:
            self.templates = []

    def save(self):
        with open(FILE_PATH, "w") as f:
            json.dump(self.templates, f, indent=4)

    def add_template(self, nume, categorie, suma, zi, descriere="", activ=True):
        self.templates.append({
            "nume": nume,
            "categorie": categorie,
            "suma": float(suma),
            "zi": int(zi),
            "descriere": descriere,
            "activ": activ
        })
        self.save()

    def update_template(self, index, data):
        if 0 <= index < len(self.templates):
            self.templates[index] = data
            self.save()

    def delete_template(self, index):
        if 0 <= index < len(self.templates):
            del self.templates[index]
            self.save()

    def get_active_templates(self):
        return [t for t in self.templates if t['activ']]