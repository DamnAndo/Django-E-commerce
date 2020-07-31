from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime


def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_item
    else:
        items = []
        order = {
            'get_cart_total':0,
            'get_cart_item':0,
            'shipping': False,
        }
        cart_items = order['get_cart_item']

    products = Product.objects.all()
    context = {
        'products':products,
        'items': items,
        'order': order,
        'cart_items':cart_items,
    }

    return render(request,'store/store.html',context)

def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_item
    else:
        print("Helllo Ando")
        try:
            cart = json.loads(request.COOKIES['cart'])
            print('CART TRY', cart)

        except:
            cart = {}
            print('CART EXCEPT',cart)


        items = []
        order = {
            'get_cart_total':0,
            'get_cart_item':0,
            'shipping': False,
        }

        cart_items = order['get_cart_item']

        for i in cart:
            cart_items += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_item'] += cart[i]['quantity']
            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                },
                'quantity':cart[i]['quantity'],
                'get_total':total,
            }

            items.append(item)

    context = {
        'items':items,
        'order':order,
        'cart_items': cart_items,
    }

    return render(request,'store/cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_item

    else:
        items = []
        order = {
            'get_cart_total':0,
            'get_cart_item':0,
            'shipping': False,
        }
        cart_items = order['get_cart_item']

    context = {
        'items':items,
        'order':order,
        'cart_items': cart_items,
    }
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print("Action : ",action)
    print("Product Id : ",productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity+1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity-1

    orderItem.save()

    if orderItem.quantity<=0:
        orderItem.delete()

    return JsonResponse('Item was added ',safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        pass
        # customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zip_code=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)
