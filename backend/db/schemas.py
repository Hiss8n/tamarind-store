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


class CheckoutItem(BaseModel):
	product_id: int = Field(gt=0)
	name: str = Field(min_length=1, max_length=120)
	quantity: int = Field(gt=0)
	price: float = Field(gt=0)
	


class CheckoutCreate(OrderCreate):
	name: str = Field(min_length=1, max_length=120)
	phone: str = Field(min_length=1, max_length=20)
	items: list[CheckoutItem]


class OrderRead(OrderCreate):
	model_config = ConfigDict(from_attributes=True)

	order_id: int = Field(gt=0)
	product_id: int = Field(gt=0)
	unit: int = Field(gt=0)
	payer_name: str = ""
	payer_phone: str = ""


class CheckoutRead(BaseModel):
	order_ids: list[int]
	total_price: float
	status: str
	payer_name: str
	payer_phone: str


