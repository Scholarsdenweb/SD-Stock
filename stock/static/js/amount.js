quantityInput = document.getElementById('id_quantity')
unitPriceInput = document.getElementById('id_unit_price')
amountInput = document.getElementById('id_total_amount')

items = document.getElementById('id_item')



unitPriceInput.addEventListener('input', (e) => {
    total =( e.target.value * quantityInput.value)
    amountInput.value = total
})

quantityInput.addEventListener('input', (e) => {
    total =( e.target.value * unitPriceInput.value)
    amountInput.value = total
})

// disable submit button on submit

function disableSubmitButton(){
    submitBtn = document.getElementById('submit')
    submitBtn.disabled = true
}