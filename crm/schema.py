import graphene
from graphene_django import DjangoObjectType
from crm.models import Product, Customer, Order
from graphql import GraphQLError
from django.core.exceptions import ValidationError
from django.db import transaction

# Object Types
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

# Queries
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

# Mutations

class CreateCustomer(graphene.Mutation):
    # ... your existing CreateCustomer mutation here ...

    class Arguments:
        # define input args

    # define mutate method

class BulkCreateCustomers(graphene.Mutation):
    # ... your existing BulkCreateCustomers mutation here ...

class CreateProduct(graphene.Mutation):
    # ... your existing CreateProduct mutation here ...

class CreateOrder(graphene.Mutation):
    # ... your existing CreateOrder mutation here ...

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

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)
