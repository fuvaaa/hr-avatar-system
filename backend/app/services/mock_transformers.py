class MockPipeline:
    def __init__(self, task, model=None):
        self.task = task
        self.model = model
    
    def __call__(self, text, **kwargs):
        if self.task == "sentiment-analysis":
            # Возвращаем случайный результат для анализа тональности
            return [{"label": "POSITIVE", "score": 0.9}]
        elif self.task == "text-generation":
            # Возвращаем простой текст
            return [{"generated_text": "Это сгенерированный текст."}]
        return [{"result": "Mock result"}]

class MockAutoModelForSequenceClassification:
    @staticmethod
    def from_pretrained(model_name):
        return MockModel()

class MockModel:
    def __call__(self, *args, **kwargs):
        return MockOutput()

class MockOutput:
    def __init__(self):
        self.logits = [[0.1, 0.9]]
        self.hidden_states = None

class MockAutoTokenizer:
    @staticmethod
    def from_pretrained(model_name):
        return MockTokenizer()

class MockTokenizer:
    def __call__(self, text, **kwargs):
        return {"input_ids": [1, 2, 3], "attention_mask": [1, 1, 1]}
    
    def decode(self, token_ids):
        return "Декодированный текст"

class MockAutoModel:
    @staticmethod
    def from_pretrained(model_name):
        return MockModel()