class MockProvider:
    async def create_avatar(self, image_asset_id: str) -> str:
        raise NotImplementedError("Mock provider does not generate images")

    async def create_tryon(self, avatar_asset_id: str, garment_asset_id: str) -> str:
        raise NotImplementedError("Mock provider does not generate images")
