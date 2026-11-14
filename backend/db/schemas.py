from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
	name: str = Field(min_length=1, max_length=120)
	description: str = Field(min_length=1, max_length=500)
	price: float = Field(gt=0)
	image: str = Field(min_length=1, max_length=2048)
	image_alt: str = Field(min_length=1, max_length=255)
	tag: str = Field(min_length=1, max_length=80)


class ProductRead(ProductCreate):
	model_config = ConfigDict(from_attributes=True)

	product_id: int = Field(gt=0)


class OrderCreate(BaseModel):
	total_price: float = Field(gt=0)
	status: str = Field(default="pending", min_length=1, max_length=30)


class OrderRead(OrderCreate):
	model_config = ConfigDict(from_attributes=True)

	order_id: int = Field(gt=0)


class CartItemCreate(BaseModel):
	name: str = Field(min_length=1, max_length=120)
	count: int = Field(gt=0)
	price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class CartItemRead(BaseModel):
	name: str
	count: int
	price: Decimal
	total_price: Decimal


class CartRead(BaseModel):
	items: list[CartItemRead]
	total_price: Decimal
