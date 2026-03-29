from fastapi.responses import JSONResponse


class ApiResponder:
    def __init__(self):
        self.payload = None

    async def send(self, content: str):
        self.payload = {"message": content}

    def response(self):
        return JSONResponse(content=self.payload or {"message": ""})
