import graphene


import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from graphql import GraphQLError

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query)

# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Input Types
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

# Mutations
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
            customer.full_clean()  # Runs validations
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except ValidationError as e:
            if 'email' in e.message_dict:
                raise GraphQLError("A customer with this email already exists.")
            if 'phone' in e.message_dict:
                raise GraphQLError("Invalid phone number format. Use '+1234567890' or '123-456-7890'")
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
            # Validate customer exists
            customer = Customer.objects.get(pk=input.customer_id)
            
            # Validate products exist and get them
            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    raise GraphQLError(f"Product with ID {product_id} does not exist")
            
            if not products:
                raise GraphQLError("At least one product is required")
            
            # Create the order
            order = Order(customer=customer)
            order.save()  # Save first to get an ID
            
            # Add products and calculate total
            order.products.set(products)
            order.total_amount = sum(product.price for product in products)
            order.save()
            
            return CreateOrder(order=order)
        except Customer.DoesNotExist:
            raise GraphQLError(f"Customer with ID {input.customer_id} does not exist")
        except Exception as e:
            raise GraphQLError(str(e))

# Combine all mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Query definitions
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

schema = graphene.Schema(query=Query, mutation=Mutation)
