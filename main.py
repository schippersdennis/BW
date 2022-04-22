__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

import models
from playhouse.shortcuts import *
from rich.console import Console
from rich.table import Table
import peewee
from flask import jsonify


def main():

    console = Console()

    # (Cast to string only for printing out results in rich tables.)
    # (Made a custom validation on data because library didnt install correctly.)

    def search(term) -> models.Product:
        # Query
        q = models.Product.select().where(
            fn.lower(models.Product.product_name) == fn.lower(term)
        )
        if q.exists():
            product = q.get()
            # Render table.
            table = Table(title="Search Products")
            for key in models.Product._meta.fields.keys():
                table.add_column(key)
            table.add_row(
                str(product.id),
                product.product_name,
                product.description,
                str(product.price),
                str(product.quantity),
                str(product.product_owner_id),
            )
            console.print(table)
            return {"success": 200, "data": model_to_dict(product)}
        else:
            return {"success": 200, "message": "Nothing Found."}

    def list_user_products(user_id) -> models.User:
        # Query
        user = models.User.select().where(models.User.id == user_id).get()

        # Render table.
        table = Table(title=f"{user.user_name} products")
        for key in models.Product._meta.fields.keys():
            table.add_column(key)
        table.add_column("user_name")
        for item in user.get_products:
            print(item.product_name)
            table.add_row(
                str(item.id),
                item.product_name,
                item.description,
                str(item.price),
                str(item.quantity),
                str(item.product_owner_id),
                user.user_name,
            )
        console.print(table)

    def list_products_per_tag(tag_id) -> models.ProductTag:

        products = (
            models.Product.select()
            .join(models.ProductTag)
            .join(models.Tag)
            .where(fn.lower(models.Tag.tag_name) == fn.lower(tag_id))
        )

        if products.exists():
            # Render table.
            table = Table(title=f"Products with tag:{tag_id}")
            for key in models.Product._meta.fields.keys():
                table.add_column(key)
            table.add_column("tag_name")

            for item in products:
                table.add_row(
                    str(item.id),
                    item.product_name,
                    item.description,
                    str(item.price),
                    str(item.quantity),
                    str(item.product_owner_id),
                    tag_id,
                )
            console.print(table)
            return {"success": 200, "data": list(products)}

        else:
            return {"success": 200, "message": "Nothing Found."}

    def add_product_to_catalog(user_id, product) -> models.Product:
        # Custom validation on input.
        if (
            (product["product_name"] and isinstance(product["product_name"], str))
            and (product["description"] and isinstance(product["description"], str))
            and (product["price"] and isinstance(product["price"], float))
            and (product["quantity"] and isinstance(product["quantity"], int))
            and (product["tags"] and isinstance(product["tags"], list))
            and (user_id and isinstance(user_id, int))
        ):
            # Check if user excist.
            if not models.User.select().where(models.User.id == user_id):
                return {"Not found": 404, "error": "No user found"}

            # Add product
            new_product = models.Product(
                product_name=product["product_name"],
                description=product["description"],
                price=product["price"],
                quantity=product["quantity"],
                product_owner_id=user_id,
            )

            new_product.save()

            # Add Tags
            for tag in product["tags"]:
                if tag and isinstance(tag, str):
                    q = models.Tag.select().where(
                        fn.Lower(models.Tag.tag_name) == fn.lower(tag)
                    )
                    if not (q.exists()):
                        tag = models.Tag(tag_name=tag)
                        tag.save()
                        p_tag = models.ProductTag(
                            product_id=new_product.id, tag_id=tag.id
                        )
                        p_tag.save()
                    else:
                        p_tag = models.ProductTag(
                            product_id=new_product.id, tag_id=q.get().id
                        )
                        p_tag.save()
            return {
                "success": 200,
                "data": model_to_dict(p_tag),
            }
        else:
            return {"bad-request": 400, "error": "Type or input error."}

    def update_stock(product_id, new_quantity) -> models.Product:
        models.Product.update({models.Product.quantity: new_quantity}).where(
            models.Product.id == product_id
        ).execute()

        return {"success": 200, "message": "Quantity changed"}

    def purchase_product(product_id, buyer_id, quantity):
        if not models.Product.select().where(models.Product.id == product_id):
            return {"Bad Request": 404, "message": "Product Not Found"}

        if not models.User.select().where(models.User.id == buyer_id):
            return {"Bad Request": 404, "message": "User Not Found"}

        product = models.Product.select().where(models.Product.id == product_id).get()

        if product.quantity >= quantity:
            product.quantity = product.quantity - quantity
            new_transaction = models.Transaction(
                seller_id=product.product_owner,
                buyer_id=buyer_id,
                product_id=product_id,
                quantity=quantity,
            )
            product.save()
            new_transaction.save()

            return {"success": 200, "message": "Product Purchased"}
        else:

            return {
                "Success": 200,
                "message": f"Product sold-out only {product.quantity} in stock",
            }

    def remove_product(product_id) -> models.Product:
        if not (product_id and isinstance(product_id, int)):
            return {"bad-request": 400, "error": "Type or input error."}

        if not models.Product.select().where(models.Product.id == product_id):
            return {"Bad Request": 404, "message": "Product Not Found"}

        models.Product.delete_by_id(product_id)

        return {"success": 200, "message": "Product Deleted"}

    # print(search("Get"))
    # list_user_products(9)
    print(list_products_per_tag("guessnear"))

    # print(
    #     add_product_to_catalog(
    #         3,
    #         {
    #             "product_name": "a",
    #             "description": "123a4asd56",
    #             "price": 121.65,
    #             "quantity": 1124,
    #             "tags": ["himas"],
    #         },
    #     )
    # )

    # print(update_stock(3, 8000))
    # print(purchase_product(9, 1, 3))
    # print(remove_product())


if __name__ == "__main__":
    main()
