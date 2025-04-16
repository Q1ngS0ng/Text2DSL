import json

class file_prase:
    def __init__(self, file):
        self.file = self.prase_file(file)

    def prase_file(self,file):
        data = json.load(file)
        return data

    def prase_keys(self):
        data = self.file.keys()
        return data

if __name__ == "__main__":
    file = file_prase("dataset/key_value_example.json")
    print(file.file)
    print(file.prase_keys())