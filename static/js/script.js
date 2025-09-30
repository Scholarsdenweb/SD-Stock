const modal = document.getElementById('id_stockform_modal')
const addMoreBtn = document.getElementById('id_add_more')
const stockForm = document.querySelector('#stock_form')

$('#test-select').select2()

if(modal){

    modal.addEventListener('hide.bs.modal', () => {
        // clear form
        const stockDetailHtml = document.getElementById('response_message')
        window.location.reload()
        stockForm.reset()
        while (stockDetailHtml.firstChild) {
            stockDetailHtml.removeChild(stockDetailHtml.firstChild);
        }
    })
}

document.body.addEventListener('htmx:afterRequest', function (evt) {
    if (evt.detail.elt.id === 'stock_form') {
        document.querySelector('#stock_form').reset();
    }
});

let inputAdded = false
document.body.addEventListener('htmx:afterSwap', function(event) {
    $('.variant-select').select2({});
    const serialEditorForm = document.getElementById('serial_editor_form')
    const overrideBtn = document.querySelector('#override_btn')

    const addMoreBtn = document.getElementById('add_more_btn')
    const columnCount = document.querySelector("input[name='column_count']");

    if(addMoreBtn){

        addMoreBtn.addEventListener('click', () => {
    
            for (let i = 1; i < columnCount.value ; i++) {
                event.detail.elt.insertAdjacentHTML('beforeend', `<div class="mt-2 serial-input d-flex gap-3">
                <input type="text" required name="serial" placeholder="Enter serial number">
                <button type="button" class="btn btn-close border border-1 border-danger bg-danger text-white rounded-circle btn-danger"
                onclick="this.closest('.serial-input').remove()"></button>
                </div>`)
            }
        })
    }

});



let sku = document.querySelector('#id_is_serialized')
let serialContainer = document.querySelector('#serial_container')


// if(sku) {
//    sku.addEventListener('change', (e) => { 

//         if(e.target.checked){
//             let inputElement = document.createElement('input')
//             inputElement.setAttribute('type', 'text')
//             inputElement.setAttribute('name', 'is_serialized')
//             inputElement.setAttribute('class', 'form-control')
//             inputElement.setAttribute('id', 'id_serial_number')
//             inputElement.setAttribute('placeholder', 'Serial Number')
//             serialContainer.appendChild(inputElement)
//         }
//         else{
//             const serialInput = document.querySelector('#id_serial_number')
//             serialContainer.removeChild(serialInput)
//         }
//    })
// }


document.body.addEventListener('htmx:afterSwap', () => {
    const returnForm = document.querySelector('#returnform')
    const listWraper = document.querySelector('.list-wraper')
    const refreshBtn = document.querySelector('#refreshbtn')

    if(refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            returnForm.reset()
        })
    }


})



function disableSubmitButton(){
    const stockEditForm = document.querySelector('.edit_stock_form')
    const submitButton = stockEditForm.getElementsByTagName('button')[0]
    const selectElements = stockEditForm.querySelectorAll('select')

    submitButton.disabled = true

    if(stockEditForm){
        let selectedItems = []
        selectElements.forEach(dropdown => {
            selectedItems.push(dropdown.selectedIndex)

            console.log(selectedItems)
            dropdown.addEventListener('change', (e) => {
              if(selectedItems.includes(e.target.selectedIndex)){
                submitButton.disabled = true
              }else{
                submitButton.disabled = false
              }
           })
       })
    }
}

disableSubmitButton()




