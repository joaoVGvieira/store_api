from typing import List
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import NotFoundException


class ProductUsecase:
    def __init__(self) -> None:
        self.client = db_client.get()
        self.collection = self.client["products"]

    async def create(self, body: ProductIn) -> ProductOut:
        product_model = ProductModel(**body.dict())
        await self.collection.insert_one(product_model.dict())
        return ProductOut(**product_model.dict())

    async def get(self, id: str) -> ProductOut:
        result = await self.collection.find_one({"_id": id})
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return ProductOut(**result)

    async def query(self, min_price: float = None, max_price: float = None) -> List[ProductOut]:
        query = {}
        if min_price is not None:
            query["price"] = {"$gt": min_price}
        if max_price is not None:
            query["price"].update({"$lt": max_price})

        products = await self.collection.find(query).to_list(length=None)
        return [ProductOut(**product) for product in products]

    async def update(self, id: str, body: ProductUpdate) -> ProductUpdateOut:
        result = await self.collection.find_one_and_update(
            filter={"_id": id},
            update={"$set": body.dict(exclude_unset=True)},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return ProductUpdateOut(**result)

    async def delete(self, id: str) -> bool:
        product = await self.collection.find_one({"_id": id})
        if not product:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        result = await self.collection.delete_one({"_id": id})
        return True if result.deleted_count > 0 else False
