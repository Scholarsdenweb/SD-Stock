quantityInput = document.getElementById('id_quantity')
unitPriceInput = document.getElementById('id_unit_price')
amountInput = document.getElementById('id_total_amount')

unitPriceInput.addEventListener('input', (e) => {
    total =( e.target.value * quantityInput.value)
    amountInput.value = total
})

quantityInput.addEventListener('input', (e) => {
    total =( e.target.value * unitPriceInput.value)
    amountInput.value = total
})