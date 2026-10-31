


class OllamaLLMClient:

    def __init__(
        self,
        base_url: str,
        model: str,
    ):
        self.base_url = base_url
        self.model = model

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        top_p: float = 0.9,
        seed: int | None = None,
        num_predict: int = 100,
    ) -> LLMResponse:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=300.0,
        ) as client:
            options = {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": num_predict,
            }

            if seed is not None:
                options["seed"] = seed

            # Indented inside the context manager block so the client remains open
            response = await client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": options,
                    "stream": False,
                },
            )

            response.raise_for_status()
            data = response.json()

        # The mapping and return statement can happen outside the context block
        return LLMResponse(
            text=data["response"],
            model=data["model"],
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
            done_reason=data.get("done_reason"),
            total_duration_ns=data.get("total_duration"),
            load_duration_ns=data.get("load_duration"),
            prompt_eval_duration_ns=data.get("prompt_eval_duration"),
            eval_duration_ns=data.get("eval_duration"),
        )


async def generate_json(
    self,
    prompt: str,
    schema: dict,
) -> dict:
    async with httpx.AsyncClient(
        base_url=self.base_url,
        timeout=self.timeout_seconds,
    ) as client:
        response = await client.post(
            "/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": schema,
            },
        )

        response.raise_for_status()

        data = response.json()

        return json.loads(data["response"])
