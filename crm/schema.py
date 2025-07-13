import graphene
from graphene_django import DjangoObjectType
from crm.models import Product, Customer, Order
from graphql import GraphQLError
from django.core.exceptions import ValidationError
from django.db import transaction

# ------------------------
# Object Types
# ------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# ------------------------
# Queries
# ------------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

# ------------------------
# Input Types
# ------------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# ------------------------
# Mutations
# ------------------------

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except ValidationError as e:
            if 'email' in e.message_dict:
                raise GraphQLError("A customer with this email already exists.")
            if 'phone' in e.message_dict:
                raise GraphQLError("Invalid phone number format.")
            raise GraphQLError(str(e))

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, inputs):
        customers = []
        errors = []

        for input in inputs:
            try:
                customer = Customer(
                    name=input.name,
                    email=input.email,
                    phone=input.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
            except ValidationError as e:
                if 'email' in e.message_dict:
                    errors.append(f"Email {input.email} already exists")
                elif 'phone' in e.message_dict:
                    errors.append(f"Invalid phone format for {input.name}")
                else:
                    errors.append(str(e))
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input):
        try:
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock if input.stock is not None else 0
            )
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except ValidationError as e:
            if 'price' in e.message_dict:
                raise GraphQLError("Price must be a positive number")
            if 'stock' in e.message_dict:
                raise GraphQLError("Stock cannot be negative")
            raise GraphQLError(str(e))

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)

            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    raise GraphQLError(f"Product with ID {product_id} does not exist")

            if not products:
                raise GraphQLError("At least one product is required")

            order = Order(customer=customer)
            order.save()
            order.products.set(products)
            order.total_amount = sum(product.price for product in products)
            order.save()

            return CreateOrder(order=order)
        except Customer.DoesNotExist:
            raise GraphQLError(f"Customer with ID {input.customer_id} does not exist")
        except Exception as e:
            raise GraphQLError(str(e))

class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_products.append(product)
        message = f"Updated {len(updated_products)} products with low stock."
        return UpdateLowStockProducts(updated_products=updated_products, message=message)

# ------------------------
# Combined Mutation Class
# ------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)


