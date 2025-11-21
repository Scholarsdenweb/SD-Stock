def allocation_cart_count(request):
    cart = request.session.get('allocation_cart', [])
    return {
        "allocation_cart_count": len(cart)
    }
